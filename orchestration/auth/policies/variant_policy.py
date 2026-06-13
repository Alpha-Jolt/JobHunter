"""Variant policy — authorization rules for ResumeVariant records."""

from __future__ import annotations

import uuid
from typing import Any

from orchestration.auth.models.user import UserRecord
from orchestration.auth.policies.base import BasePolicy


class VariantPolicy(BasePolicy):
    """Authorization rules for ResumeVariant resources."""

    @staticmethod
    def can_release(user: UserRecord, variant: Any) -> bool:
        """User owns the variant AND variant is approved, OR Admin.

        'Release' means the variant is eligible to be sent in an application.

        Args:
            user: Authenticated user.
            variant: Object with user_id (UUID) and approval_status (str).
        """
        if BasePolicy._is_admin(user):
            return True

        variant_user_id = getattr(variant, "user_id", None)
        if isinstance(variant_user_id, str):
            try:
                variant_user_id = uuid.UUID(variant_user_id)
            except ValueError:
                return False

        if variant_user_id != user.user_id:
            return False

        return getattr(variant, "approval_status", "") == "approved"

    @staticmethod
    def can_view(user: UserRecord, variant: Any) -> bool:
        """User owns the variant OR Admin."""
        if BasePolicy._is_admin(user):
            return True

        variant_user_id = getattr(variant, "user_id", None)
        if isinstance(variant_user_id, str):
            try:
                variant_user_id = uuid.UUID(variant_user_id)
            except ValueError:
                return False

        return variant_user_id == user.user_id
