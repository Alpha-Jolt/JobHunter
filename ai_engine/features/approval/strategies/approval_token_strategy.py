"""Email-based approval token strategy for Phase 0."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from ai_engine.core.types import APPROVAL_TOKEN_TTL_HOURS, ApprovalStatus

_TOKEN_VERSION = "v1"


def generate_token(variant_id: str, user_id: str, action: ApprovalStatus, secret: str) -> str:
    """Generate a signed approval token.

    Token format: ``{version}.{payload_b64}.{signature}``
    Payload contains: variant_id, user_id, action, expires_at.

    Args:
        variant_id: Variant to approve/reject.
        user_id: User who owns the variant.
        action: ApprovalStatus.APPROVED or ApprovalStatus.REJECTED.
        secret: HMAC signing secret (from config).

    Returns:
        Signed token string.
    """
    import base64  # noqa: PLC0415

    expires_at = int(time.time()) + APPROVAL_TOKEN_TTL_HOURS * 3600
    payload = json.dumps(
        {
            "variant_id": variant_id,
            "user_id": user_id,
            "action": action.value,
            "expires_at": expires_at,
        },
        separators=(",", ":"),
    )
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{_TOKEN_VERSION}.{payload_b64}.{sig}"


def validate_token(token: str, secret: str) -> dict:
    """Validate and decode an approval token.

    Args:
        token: Token string from the approval link.
        secret: HMAC signing secret.

    Returns:
        Decoded payload dict with variant_id, user_id, action.

    Raises:
        ValueError: If token is invalid, expired, or tampered.
    """
    import base64  # noqa: PLC0415

    parts = token.split(".")
    if len(parts) != 3 or parts[0] != _TOKEN_VERSION:
        raise ValueError("Invalid token format.")

    _, payload_b64, provided_sig = parts
    expected_sig = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(provided_sig, expected_sig):
        raise ValueError("Token signature is invalid.")

    payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())

    if time.time() > payload["expires_at"]:
        raise ValueError("Token has expired.")

    return payload
