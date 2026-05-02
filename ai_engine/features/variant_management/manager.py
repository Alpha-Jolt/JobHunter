"""Variant manager orchestrator."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from ai_engine.core.exceptions import ValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.variant_management.limiters.budget_enforcer import BudgetEnforcer
from ai_engine.features.variant_management.models.variant_record import VariantRecord
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry
from ai_engine.features.variant_management.strategies.deduplication import is_duplicate

logger = get_logger(__name__)


@dataclass
class RegistrationResult:
    """Result of a variant registration attempt.

    Attributes:
        variant_id: The registered variant's ID.
        is_duplicate: Whether this was a duplicate (still registered if force=True).
    """

    variant_id: str
    is_duplicate: bool = False


class VariantManager:
    """Orchestrates variant registration with budget and deduplication checks.

    Args:
        registry: JSONRegistry (or DatabaseRegistry in Phase 0+).
        budget_enforcer: BudgetEnforcer instance.
    """

    def __init__(self, registry: JSONRegistry, budget_enforcer: BudgetEnforcer) -> None:
        self._registry = registry
        self._budget = budget_enforcer

    async def register(
        self,
        variant: OptimisedVariant,
        comparison: ComparisonResult,
        user_id: str,
        force_duplicate: bool = False,
    ) -> RegistrationResult:
        """Register a new variant after budget and deduplication checks.

        Args:
            variant: The OptimisedVariant to register.
            comparison: ComparisonResult for match score metadata.
            user_id: User identifier.
            force_duplicate: If True, register even if a variant exists for this job.

        Returns:
            RegistrationResult with the new variant_id.

        Raises:
            VariantBudgetExceededError: If budget is exhausted.
            ValidationError: If duplicate is detected and force_duplicate=False.
        """
        total_count = self._registry.count_all()
        self._budget.consume(total_count)

        existing = self._registry.list_by_job(variant.job_id)
        duplicate = is_duplicate(variant.job_id, existing)

        if duplicate and not force_duplicate:
            raise ValidationError(
                f"Variant already exists for job {variant.job_id}. "
                "Use force_duplicate=True to regenerate."
            )

        variant_id = str(uuid.uuid4())
        record = VariantRecord(
            variant_id=variant_id,
            job_id=variant.job_id,
            user_id=user_id,
            prompt_version=variant.prompt_version_used,
            match_score=comparison.match_score,
            fabrication_check_result="passed",
            approval_status=ApprovalStatus.PENDING,
        )
        self._registry.create(record)

        logger.info(
            "variant_manager.registered",
            variant_id=variant_id,
            job_id=variant.job_id,
            match_score=comparison.match_score,
        )
        return RegistrationResult(variant_id=variant_id, is_duplicate=duplicate)

    def update_approval(self, variant_id: str, status: ApprovalStatus) -> None:
        """Update the approval status of a registered variant.

        Args:
            variant_id: Variant identifier.
            status: New approval status.
        """
        self._registry.update_status(variant_id, status)
