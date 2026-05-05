"""Approval gate — blocks unapproved variants from output release."""

from __future__ import annotations

from ai_engine.core.exceptions import ApprovalRequiredError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry

logger = get_logger(__name__)


class ApprovalGate:
    """Enforces approval before any variant can be released to output.

    Args:
        registry: JSONRegistry (or DatabaseRegistry in Phase 0+).
    """

    def __init__(self, registry: JSONRegistry) -> None:
        self._registry = registry

    def check(self, variant_id: str) -> ApprovalStatus:
        """Check the approval status of a variant.

        Args:
            variant_id: Variant identifier.

        Returns:
            Current ApprovalStatus.

        Raises:
            ApprovalRequiredError: If variant is not found or not approved.
        """
        record = self._registry.get(variant_id)
        if record is None:
            raise ApprovalRequiredError(variant_id, context={"reason": "variant_not_found"})

        logger.info(
            "approval_gate.checked",
            variant_id=variant_id,
            status=record.approval_status.value,
        )
        return record.approval_status

    def require_approved(self, variant_id: str) -> None:
        """Assert that a variant is approved, raising if not.

        Args:
            variant_id: Variant identifier.

        Raises:
            ApprovalRequiredError: If variant is pending or rejected.
        """
        status = self.check(variant_id)
        if status != ApprovalStatus.APPROVED:
            raise ApprovalRequiredError(
                variant_id,
                context={"current_status": status.value},
            )
