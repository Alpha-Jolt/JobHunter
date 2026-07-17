"""Unit tests for Mail-Bridge integration.

Tests cover:
- MailBridgeClient payload construction and error handling
- Retry logic on 429 and 5xx
- Webhook signature verification
- MailService credential resolution and send flow
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from orchestration.services.mailbridge_client import (
    MailBridgeClient,
    MailBridgeError,
)
from orchestration.services.mail_service import MailService


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_response(status_code: int, body: dict):
    mock = MagicMock()
    mock.status_code = status_code
    mock.is_success = 200 <= status_code < 300
    mock.json.return_value = body
    mock.text = json.dumps(body)
    return mock


# ── MailBridgeClient — payload ─────────────────────────────────────────────────

class TestMailBridgeClientPayload:
    """Verify that send_email builds the correct payload for Mail-Bridge v2."""

    @pytest.mark.asyncio
    async def test_send_email_sets_bearer_header(self):
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test_abc")
        captured = {}

        async def fake_post(url, headers, json, timeout):
            captured["headers"] = headers
            captured["json"] = json
            return _make_response(202, {"success": True, "email_id": "uuid-1", "status": "queued"})

        with patch("httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)

            await client.send_email(
                credential_id="cred-uuid",
                to_email="hr@company.com",
                subject="Test",
                html="<p>Test</p>",
            )

        assert captured["headers"]["Authorization"] == "Bearer sk_test_abc"
        assert captured["json"]["credential_id"] == "cred-uuid"

    @pytest.mark.asyncio
    async def test_send_email_attachment_uses_url_key(self):
        """Attachments must use 'url' key — not 'signed_url'."""
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test")
        captured = {}

        async def fake_post(url, headers, json, timeout):
            captured["json"] = json
            return _make_response(202, {"success": True, "email_id": "uuid-2", "status": "queued"})

        with patch("httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)

            await client.send_email(
                credential_id="cred-uuid",
                to_email="hr@company.com",
                subject="Test",
                html="<p>Test</p>",
                attachments=[{"filename": "Resume.pdf", "url": "https://minio/resume.pdf"}],
            )

        att = captured["json"]["attachments"][0]
        assert "url" in att
        assert "signed_url" not in att

    @pytest.mark.asyncio
    async def test_send_email_raises_mailbridge_error_on_400(self):
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test")

        mock_resp = _make_response(400, {"success": False, "error": {"code": "VALIDATION_FAILED", "message": "Missing variable"}})

        with patch("httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(return_value=mock_resp)

            with pytest.raises(MailBridgeError) as exc_info:
                await client.send_email(
                    credential_id="cred",
                    to_email="hr@company.com",
                    subject="Test",
                    html="<p>test</p>",
                )

        assert exc_info.value.code == "VALIDATION_FAILED"
        assert exc_info.value.status == 400

    @pytest.mark.asyncio
    async def test_send_batch_raises_on_over_100(self):
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test")
        emails = [{"credential_id": "c", "to_email": f"u{i}@test.com"} for i in range(101)]
        with pytest.raises(MailBridgeError) as exc_info:
            await client.send_batch(emails)
        assert exc_info.value.code == "BATCH_TOO_LARGE"


# ── MailBridgeClient — retry ───────────────────────────────────────────────────

class TestMailBridgeClientRetry:
    """Retry logic: back off on 429 / 5xx, raise immediately on 4xx."""

    @pytest.mark.asyncio
    async def test_retries_on_429_and_eventually_succeeds(self):
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test")
        call_count = 0

        async def fake_post(url, headers, json, timeout):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return _make_response(429, {"success": False, "error": {"code": "RATE_LIMIT", "message": "slow down"}})
            return _make_response(202, {"success": True, "email_id": "uuid-ok", "status": "queued"})

        with patch("httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)
            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await client.send_email(
                    credential_id="cred",
                    to_email="hr@test.com",
                    subject="Test",
                    html="<p>x</p>",
                )

        assert call_count == 3
        assert result["email_id"] == "uuid-ok"

    @pytest.mark.asyncio
    async def test_raises_after_max_retries_on_500(self):
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test")

        with patch("httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(return_value=_make_response(500, {"success": False, "error": {"code": "INTERNAL", "message": "boom"}}))
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(MailBridgeError) as exc_info:
                    await client.send_email(
                        credential_id="cred",
                        to_email="hr@test.com",
                        subject="Test",
                        html="<p>x</p>",
                    )

        assert exc_info.value.code == "MAX_RETRIES"

    @pytest.mark.asyncio
    async def test_does_not_retry_on_401(self):
        """401 is not retryable — should raise immediately."""
        client = MailBridgeClient(base_url="http://localhost:3009", api_key="sk_test")
        call_count = 0

        async def fake_post(url, headers, json, timeout):
            nonlocal call_count
            call_count += 1
            return _make_response(401, {"success": False, "error": {"code": "INVALID_TOKEN", "message": "bad key"}})

        with patch("httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.post = AsyncMock(side_effect=fake_post)

            with pytest.raises(MailBridgeError) as exc_info:
                await client.send_email(
                    credential_id="cred",
                    to_email="hr@test.com",
                    subject="Test",
                    html="<p>x</p>",
                )

        assert call_count == 1
        assert exc_info.value.status == 401


# ── Webhook signature ─────────────────────────────────────────────────────────

class TestWebhookSignature:
    """verify_mailbridge_signature must use compare_digest."""

    def _make_sig(self, body: bytes, secret: str) -> str:
        return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    def test_valid_signature_returns_true(self):
        from orchestration.api.routes.webhooks import _verify_signature

        body = b'{"event":"email.sent","email_id":"abc"}'
        secret = "super-secret-webhook-key-32chars!"
        sig = self._make_sig(body, secret)
        assert _verify_signature(body, sig, secret) is True

    def test_tampered_body_returns_false(self):
        from orchestration.api.routes.webhooks import _verify_signature

        body = b'{"event":"email.sent","email_id":"abc"}'
        tampered = b'{"event":"email.sent","email_id":"EVIL"}'
        secret = "super-secret-webhook-key-32chars!"
        sig = self._make_sig(body, secret)
        assert _verify_signature(tampered, sig, secret) is False

    def test_wrong_secret_returns_false(self):
        from orchestration.api.routes.webhooks import _verify_signature

        body = b'{"event":"email.sent"}'
        secret = "correct-secret-webhook-key-32char"
        sig = self._make_sig(body, "wrong-secret-webhook-key-32chars")
        assert _verify_signature(body, sig, secret) is False


# ── MailService credential lookup ─────────────────────────────────────────────

class TestMailServiceCredentialLookup:
    """send_application should raise MailSendError when no credential is set."""

    @pytest.mark.asyncio
    async def test_raises_when_no_credential(self):
        from orchestration.core.exceptions import MailSendError

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = MailService(
            mailbridge_client=AsyncMock(),
            job_registry=AsyncMock(),
            variant_registry=AsyncMock(),
            application_log=AsyncMock(),
            db_session=mock_session,
            s3_client=MagicMock(),
        )

        # Mock variant as approved so we reach the credential check
        mock_variant = MagicMock()
        mock_variant.approval_status = "approved"
        service._variant_registry.get = AsyncMock(return_value=mock_variant)
        service._application_log.has_user_applied_to_job = AsyncMock(return_value=False)
        service._application_log.get_applications_sent_today = AsyncMock(return_value=[])

        mock_job = MagicMock()
        mock_job.apply_email = "hr@company.com"
        mock_job.status = "open"
        mock_job.title = "Engineer"
        mock_job.company_name = "Acme"
        service._job_registry.get = AsyncMock(return_value=mock_job)

        with pytest.raises(MailSendError, match="no connected mail account"):
            await service.send_application(
                user_id="user-1",
                job_id="job-1",
                variant_id="var-1",
                user_name="Alice",
                user_email="alice@example.com",
                user_phone="+91 99999 99999",
                user_summary="Software engineer",
            )
