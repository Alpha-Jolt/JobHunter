"""Mail-Bridge v2 HTTP client.

Pure outbound HTTP adapter — no business logic.
All methods raise MailBridgeError on non-2xx responses.
Exponential backoff retry is applied automatically on 429 and 5xx.
"""

import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3


class MailBridgeError(Exception):
    """Raised when Mail-Bridge returns a non-2xx response."""

    def __init__(self, code: str, message: str, status: int) -> None:
        self.code = code
        self.message = message
        self.status = status
        super().__init__(f"[{code}] {message}")


def _raise_for_error(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        body = response.json()
        err = body.get("error", {})
        raise MailBridgeError(
            code=err.get("code", "UNKNOWN"),
            message=err.get("message", response.text),
            status=response.status_code,
        )
    except (ValueError, KeyError):
        raise MailBridgeError("HTTP_ERROR", response.text[:256], response.status_code)


def _is_retryable(status: int) -> bool:
    return status == 429 or status >= 500


async def _with_retry(coro_fn, *args, **kwargs):
    """Execute an async callable with exponential backoff on retryable errors."""
    last_exc: MailBridgeError | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            return await coro_fn(*args, **kwargs)
        except MailBridgeError as exc:
            if not _is_retryable(exc.status):
                raise
            last_exc = exc
            wait = 2 ** attempt
            logger.warning(
                "mailbridge_retry",
                extra={
                    "attempt": attempt + 1,
                    "status": exc.status,
                    "code": exc.code,
                    "wait_seconds": wait,
                },
            )
            await asyncio.sleep(wait)
    raise MailBridgeError("MAX_RETRIES", "Exceeded retry limit", 0) from last_exc


class MailBridgeClient:
    """HTTP client for the Mail-Bridge v2 REST API.

    Args:
        base_url: Gateway URL, e.g. ``https://app.myjobhunter.in``.
        api_key: Bearer API key (``sk_...``).
        timeout: Per-request timeout in seconds.
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self._timeout = timeout

    # ── internal ─────────────────────────────────────────────────────────────

    async def _post(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._base_url}{path}",
                headers=self._headers,
                json=payload,
            )
        _raise_for_error(response)
        return response.json()

    async def _get(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self._base_url}{path}",
                headers=self._headers,
            )
        _raise_for_error(response)
        return response.json()

    async def _delete(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.delete(
                f"{self._base_url}{path}",
                headers=self._headers,
            )
        _raise_for_error(response)
        return response.json()

    # ── public API ────────────────────────────────────────────────────────────

    async def send_email(
        self,
        *,
        credential_id: str,
        to_email: str,
        subject: Optional[str] = None,
        html: Optional[str] = None,
        template_id: Optional[str] = None,
        variables: Optional[dict] = None,
        attachments: Optional[list[dict]] = None,
    ) -> dict:
        """Send a single email.

        Either ``template_id`` or both ``subject`` + ``html`` are required.
        ``attachments`` items must have ``filename`` and ``url`` keys —
        Mail-Bridge fetches the file content from the URL.

        Returns:
            ``{"success": true, "email_id": "<uuid>", "status": "queued"}``
        """
        payload: dict = {
            "credential_id": credential_id,
            "to_email": to_email,
        }
        if template_id:
            payload["template_id"] = template_id
        if subject:
            payload["subject"] = subject
        if html:
            payload["html"] = html
        if variables:
            payload["variables"] = variables
        if attachments:
            payload["attachments"] = attachments

        async def _call():
            return await self._post("/api/emails/send", payload)

        return await _with_retry(_call)

    async def send_batch(self, emails: list[dict]) -> dict:
        """Send up to 100 emails in a single request.

        Each item in ``emails`` follows the same shape as ``send_email`` payload.

        Returns:
            ``{"success": true, "queued": N, "email_ids": [...]}``
        """
        if len(emails) > 100:
            raise MailBridgeError("BATCH_TOO_LARGE", "Batch exceeds 100 emails", 400)

        async def _call():
            return await self._post("/api/emails/batch", {"emails": emails})

        return await _with_retry(_call)

    async def schedule_email(self, payload: dict) -> dict:
        """Schedule a future email send.

        ``payload`` must include ``scheduled_at`` (ISO8601 UTC future timestamp).

        Returns:
            ``{"success": true, "scheduled_id": "<uuid>", "scheduled_at": "..."}``
        """
        async def _call():
            return await self._post("/api/emails/schedule", payload)

        return await _with_retry(_call)

    async def cancel_schedule(self, scheduled_id: str) -> dict:
        """Cancel a pending scheduled email.

        Returns:
            ``{"success": true}``
        """
        async def _call():
            return await self._delete(f"/api/emails/schedule/{scheduled_id}")

        return await _with_retry(_call)

    async def get_email(self, email_id: str) -> dict:
        """Retrieve a single email log by ID.

        Returns the full email log record from Mail-Bridge.
        """
        async def _call():
            return await self._get(f"/api/emails/{email_id}")

        return await _with_retry(_call)

    async def list_credentials(self) -> dict:
        """List all active credentials in the workspace.

        Returns:
            ``{"success": true, "credentials": [...]}``
        """
        async def _call():
            return await self._get("/api/credentials/")

        return await _with_retry(_call)

    async def register_gmail_watch(self, credential_id: str) -> dict:
        """Re-register Gmail Pub/Sub watch for a credential.

        Should be called every ≤6 days as Gmail watch expires after 7 days.

        Returns:
            ``{"success": true}``
        """
        async def _call():
            return await self._post(f"/api/credentials/{credential_id}/watch", {})

        return await _with_retry(_call)
