"""Approval Service — HMAC-signed token generation and validation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from shared.models.exceptions import VariantNotFoundError  # noqa: F401
from shared.registries.base import VariantRegistryBase
from shared.models.variant_record import VariantRecord


class TokenInvalidError(Exception):
    """Raised when an approval token fails signature or format validation."""


class TokenExpiredError(Exception):
    """Raised when an approval token is older than the allowed TTL."""


class TokenAlreadyUsedError(Exception):
    """Raised when an approval token is used on an already-processed variant."""


class ApprovalService:
    """Generates and validates HMAC-signed approval tokens.

    Token format: ``{variant_id}:{timestamp}:{base64_signature}``

    Args:
        variant_registry: VariantRegistryBase for status lookups.
        secret_key: HMAC secret (≥32 characters).
        token_expiry_seconds: Token TTL in seconds (default 86400 = 24 h).
    """

    def __init__(
        self,
        variant_registry: Optional[VariantRegistryBase],
        secret_key: str,
        token_expiry_seconds: int = 86400,
    ) -> None:
        self.variant_registry = variant_registry
        self._secret = secret_key.encode()
        self.token_expiry_seconds = token_expiry_seconds

    # ── Token generation ──────────────────────────────────────────────────────

    def generate_approval_token(self, variant_id: str, user_email: str) -> str:
        """Generate a signed approval token.

        Args:
            variant_id: UUID string of the variant.
            user_email: User email (included in audit log, not in token).

        Returns:
            Token string: ``{variant_id}:{timestamp}:{base64_sig}``.
        """
        timestamp = int(time.time())
        message = f"{variant_id}:{timestamp}".encode()
        sig = hmac.new(self._secret, message, hashlib.sha256).digest()
        b64_sig = base64.urlsafe_b64encode(sig).decode()
        return f"{variant_id}:{timestamp}:{b64_sig}"

    # ── Token validation ──────────────────────────────────────────────────────

    def validate_approval_token(self, token: str) -> str:
        """Validate a token and return the variant_id if valid.

        Args:
            token: Token string from the approval link.

        Returns:
            variant_id string.

        Raises:
            TokenInvalidError: Malformed token or signature mismatch.
            TokenExpiredError: Token is older than token_expiry_seconds.
        """
        parts = token.split(":")
        if len(parts) != 3:
            raise TokenInvalidError("Malformed token: expected 3 colon-separated parts")

        variant_id, ts_str, provided_sig = parts

        try:
            timestamp = int(ts_str)
        except ValueError as exc:
            raise TokenInvalidError("Malformed token: invalid timestamp") from exc

        # Recompute HMAC
        message = f"{variant_id}:{timestamp}".encode()
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(self._secret, message, hashlib.sha256).digest()
        ).decode()

        if not secrets.compare_digest(expected_sig, provided_sig):
            raise TokenInvalidError("Token signature mismatch")

        # Check expiry
        if (int(time.time()) - timestamp) >= self.token_expiry_seconds:
            raise TokenExpiredError("Approval token has expired")

        return variant_id

    # ── Approval ──────────────────────────────────────────────────────────────

    async def mark_approved(self, variant_id: str) -> VariantRecord:
        """Mark a variant as approved.

        Args:
            variant_id: UUID string of the variant.

        Returns:
            Updated VariantRecord.

        Raises:
            VariantNotFoundError: If variant does not exist.
            TokenAlreadyUsedError: If variant is not in pending state.
        """
        vid = uuid.UUID(variant_id)
        record = await self.variant_registry.get(vid)

        if record.approval_status != "pending":
            raise TokenAlreadyUsedError(
                f"Variant {variant_id} is already {record.approval_status}"
            )

        now = datetime.now(timezone.utc)
        await self.variant_registry.update_approval_status(vid, "approved")

        # Reflect change in the returned record
        record.approval_status = "approved"
        record.approved_at = now
        return record
