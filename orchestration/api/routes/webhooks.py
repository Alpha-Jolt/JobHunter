# orchestration/api/routes/webhooks.py

"""Mail-Bridge webhook receiver.

Accepts HMAC-signed POST requests from Mail-Bridge and updates application
delivery status in the database.

This endpoint is called by Mail-Bridge — it must NOT be protected by the JWT
middleware.  Authenticity is verified using the HMAC-SHA256 signature on the
raw request body.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.config import get_settings, Settings
from orchestration.api.dependencies import get_db_session
from orchestration.repositories.postgres_application_repository import (
    PostgresApplicationRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _verify_signature(raw_body: bytes, signature_header: str, secret: str) -> bool:
    """Verify the X-Mail-Bridge-Signature header.

    Uses hmac.compare_digest to prevent timing attacks.
    """
    expected = "sha256=" + hmac.new(
        secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@router.post("/mailbridge")
async def mailbridge_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> Response:
    """Receive delivery status events from Mail-Bridge.

    Supported events:
    - ``email.sent``    → marks application email_delivery_status = 'delivered'
    - ``email.failed``  → marks application email_delivery_status = 'failed'
    - ``email.received``→ logs inbound reply (stored for future mailbox feature)
    """
    raw_body = await request.body()
    signature = request.headers.get("x-mail-bridge-signature", "")
    secret = settings.mail.mailbridge_webhook_secret

    if secret and not _verify_signature(raw_body, signature, secret):
        logger.warning(
            "mailbridge_webhook_invalid_signature",
            extra={"signature": signature[:32]},
        )
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        event = json.loads(raw_body)
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type: str = event.get("event", "")
    email_id: str = event.get("email_id", "")

    repo = PostgresApplicationRepository(session)

    if event_type == "email.sent":
        sent_at_raw = event.get("sent_at")
        delivered_at: datetime | None = None
        if sent_at_raw:
            try:
                delivered_at = datetime.fromisoformat(
                    sent_at_raw.replace("Z", "+00:00")
                )
            except ValueError:
                pass

        if email_id:
            await repo.update_email_delivery(
                mailbridge_email_id=email_id,
                delivery_status="delivered",
                delivered_at=delivered_at,
            )
            logger.info(
                "webhook_email_sent",
                extra={"email_id": email_id, "delivered_at": sent_at_raw},
            )

    elif event_type == "email.failed":
        if email_id:
            await repo.update_email_delivery(
                mailbridge_email_id=email_id,
                delivery_status="failed",
                delivered_at=None,
            )
            logger.warning(
                "webhook_email_failed",
                extra={
                    "email_id": email_id,
                    "error": event.get("error", ""),
                },
            )

    elif event_type == "email.received":
        # Log inbound email for future mailbox feature — non-fatal if it fails
        payload = event.get("payload", {})
        logger.info(
            "webhook_email_received",
            extra={
                "from": payload.get("from", ""),
                "subject": payload.get("subject", ""),
                "received_at": payload.get("received_at", ""),
            },
        )
        # Future: insert into inbound_emails table (Phase 7)

    else:
        logger.debug("webhook_unknown_event", extra={"event": event_type})

    return Response(status_code=200)
