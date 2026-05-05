"""Integration test: variant limit enforcement."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_engine.core.exceptions import VariantBudgetExceededError
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.variant_management.limiters.budget_enforcer import BudgetEnforcer
from ai_engine.features.variant_management.manager import VariantManager
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry


def _make_variant(job_id: str) -> OptimisedVariant:
    return OptimisedVariant(
        reordered_experience=[],
        rewritten_summary="",
        prioritized_skills=["Python"],
        selected_projects=[],
        selected_certifications=[],
        gaps=[],
        job_id=job_id,
    )


def _make_comparison() -> ComparisonResult:
    return ComparisonResult(match_score=70, matched_skills=["Python"], gap_skills=[], job_id="")


@pytest.mark.asyncio
async def test_variant_limit_enforced_at_two(tmp_path: Path):
    """Pipeline stops generating variants when limit of 2 is reached."""
    registry = JSONRegistry(tmp_path / "registry.json")
    enforcer = BudgetEnforcer(max_total=2, max_per_session=2)
    manager = VariantManager(registry, enforcer)

    await manager.register(_make_variant("job-001"), _make_comparison(), user_id="u1")
    await manager.register(_make_variant("job-002"), _make_comparison(), user_id="u1")

    with pytest.raises(VariantBudgetExceededError):
        await manager.register(_make_variant("job-003"), _make_comparison(), user_id="u1")
