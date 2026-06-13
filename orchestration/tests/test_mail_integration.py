# orchestration/tests/test_mail_integration.py

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from orchestration.services.mail_service import MailService
from orchestration.core.exceptions import (

# ── Auth test helpers ─────────────────────────────────────────────────────────
import uuid as _uuid
from datetime import datetime as _dt, timedelta as _td, timezone as _tz
from unittest.mock import patch as _patch
from orchestration.auth.tokens import encode_access_token as _encode
from orchestration.auth.models.user import RoleEnum as _RoleEnum, UserRecord as _UserRecord

_TEST_SECRET = "test-secret-key-that-is-32-chars!!"
_TEST_ALG = "HS256"

def _make_admin_user():
    return _UserRecord(
        user_id=_uuid.uuid4(), email="admin@example.com",
        password_hash="hash", role=_RoleEnum.ADMIN,
    )

def _admin_token(user=None):
    u = user or _make_admin_user()
    tok = _encode(str(u.user_id), u.role, _TEST_SECRET, _TEST_ALG,
                  _dt.now(_tz.utc) + _td(minutes=15))
    return tok, u

def _auth_headers(user=None):
    tok, u = _admin_token(user)
    return {"Authorization": f"Bearer {tok}"}, u

def _patch_auth(user=None):
    """Context manager to patch auth deps for a given user."""
    u = user or _make_admin_user()
    tok, _ = _admin_token(u)
    return _patch(
        "orchestration.auth.dependencies._get_jwt_config",
        return_value=(_TEST_SECRET, _TEST_ALG)
    ), _patch(
        "orchestration.auth.dependencies.AuthRepository"
    ), u, tok
# ─────────────────────────────────────────────────────────────────────────────

    ApprovalRequiredError,
    DuplicateApplicationError,
    RateLimitError,
    JobError,
    MailSendError,
)


def _make_variant(approval_status="approved"):
    return AsyncMock(
        variant_id="var-123",
        approval_status=approval_status,
        pdf_key="s3://resumes/var-123.pdf",
        cover_letter_id="cover-123",
    )


def _make_job(apply_email="careers@acme.com", status="open"):
    return AsyncMock(
        job_id="job-456",
        title="Python Developer",
        company_name="Acme Corp",
        location="Bangalore",
        apply_email=apply_email,
        status=status,
    )


_CALL_ARGS = dict(
    user_id="user-789",
    job_id="job-456",
    variant_id="var-123",
    user_name="Arun Kumar",
    user_email="arun@gmail.com",
    user_phone="+919876543210",
    user_summary="3 years experience in Python and FastAPI",
)


@pytest.mark.asyncio
class TestMailService:

    @pytest.fixture
    def setup(self):
        job_registry = AsyncMock()
        variant_registry = AsyncMock()
        application_log = AsyncMock()
        s3_client = MagicMock()
        s3_client.generate_presigned_url.return_value = "https://s3.example.com/signed-url"

        mail_service = MailService(
            mail_bridge_url="http://mail-bridge:3000",
            mail_bridge_api_key="test-key",
            job_registry=job_registry,
            variant_registry=variant_registry,
            application_log=application_log,
            s3_client=s3_client,
        )

        return {
            "mail_service": mail_service,
            "job_registry": job_registry,
            "variant_registry": variant_registry,
            "application_log": application_log,
            "s3_client": s3_client,
        }

    async def test_send_application_success(self, setup):
        """Full happy path: all gates pass, email sent, application recorded."""
        mail_service = setup["mail_service"]
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["job_registry"].get.return_value = _make_job()
        setup["application_log"].has_user_applied_to_job.return_value = False
        setup["application_log"].get_applications_sent_today.return_value = []

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message_id": "sendgrid-msg-id-xyz",
            "sent_at": "2026-05-06T10:30:00",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            application = await mail_service.send_application(**_CALL_ARGS)

        assert application.user_id == "user-789"
        assert str(application.job_id) == "job-456"
        assert application.status == "sent"
        assert application.thread_id == "sendgrid-msg-id-xyz"
        setup["application_log"].record_send.assert_called_once()

    async def test_send_application_not_approved(self, setup):
        """Variant is not approved → ApprovalRequiredError."""
        setup["variant_registry"].get.return_value = _make_variant("pending")

        with pytest.raises(ApprovalRequiredError):
            await setup["mail_service"].send_application(**_CALL_ARGS)

    async def test_send_application_duplicate(self, setup):
        """User already applied to this job → DuplicateApplicationError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["application_log"].has_user_applied_to_job.return_value = True

        with pytest.raises(DuplicateApplicationError):
            await setup["mail_service"].send_application(**_CALL_ARGS)

    async def test_send_application_daily_limit(self, setup):
        """User hit daily limit (10/day) → RateLimitError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["application_log"].has_user_applied_to_job.return_value = False
        setup["application_log"].get_applications_sent_today.return_value = [
            AsyncMock() for _ in range(10)
        ]

        with pytest.raises(RateLimitError) as exc_info:
            await setup["mail_service"].send_application(**_CALL_ARGS)

        assert "daily limit" in str(exc_info.value).lower()

    async def test_send_application_rate_limit_fast(self, setup):
        """Sends too fast (< 30s) → RateLimitError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["application_log"].has_user_applied_to_job.return_value = False

        recent = AsyncMock()
        recent.sent_at = datetime.utcnow()
        setup["application_log"].get_applications_sent_today.return_value = [recent]

        with pytest.raises(RateLimitError) as exc_info:
            await setup["mail_service"].send_application(**_CALL_ARGS)

        assert "wait" in str(exc_info.value).lower() or "seconds" in str(exc_info.value).lower()

    async def test_send_application_job_not_found(self, setup):
        """Job not found → JobError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["application_log"].has_user_applied_to_job.return_value = False
        setup["application_log"].get_applications_sent_today.return_value = []
        setup["job_registry"].get.side_effect = Exception("not found")

        with pytest.raises(JobError):
            await setup["mail_service"].send_application(**_CALL_ARGS)

    async def test_send_application_job_no_email(self, setup):
        """Job has no apply_email → JobError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["application_log"].has_user_applied_to_job.return_value = False
        setup["application_log"].get_applications_sent_today.return_value = []
        setup["job_registry"].get.return_value = _make_job(apply_email=None)

        with pytest.raises(JobError) as exc_info:
            await setup["mail_service"].send_application(**_CALL_ARGS)

        assert "contact email" in str(exc_info.value).lower()

    async def test_send_application_job_closed(self, setup):
        """Job is closed → JobError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["application_log"].has_user_applied_to_job.return_value = False
        setup["application_log"].get_applications_sent_today.return_value = []
        setup["job_registry"].get.return_value = _make_job(status="closed")

        with pytest.raises(JobError) as exc_info:
            await setup["mail_service"].send_application(**_CALL_ARGS)

        assert "closed" in str(exc_info.value).lower()

    async def test_send_application_mail_bridge_fails(self, setup):
        """Mail-Bridge returns error → MailSendError."""
        setup["variant_registry"].get.return_value = _make_variant("approved")
        setup["job_registry"].get.return_value = _make_job()
        setup["application_log"].has_user_applied_to_job.return_value = False
        setup["application_log"].get_applications_sent_today.return_value = []

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "error": {"code": "SEND_FAILED", "message": "Provider error"},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            with pytest.raises(MailSendError):
                await setup["mail_service"].send_application(**_CALL_ARGS)

        setup["application_log"].record_send.assert_not_called()
