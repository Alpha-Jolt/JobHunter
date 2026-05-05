"""Unit tests for variant manager."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_engine.core.exceptions import ValidationError, VariantBudgetExceededError
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.variant_management.limiters.budget_enforcer import BudgetEnforcer
from ai_engine.features.variant_management.manager import VariantManager
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry


def _make_variant(job_id: str = "job-001") -> OptimisedVariant:
    return OptimisedVariant(
        reordered_experience=[],
        rewritten_summary="Test summary",
        prioritized_skills=["Python"],
        selected_projects=[],
        selected_certifications=[],
        gaps=["Kubernetes"],
        job_id=job_id,
    )


def _make_comparison(score: int = 75) -> ComparisonResult:
    return ComparisonResult(
        match_score=score,
        matched_skills=["Python"],
        gap_skills=["Kubernetes"],
        job_id="job-001",
    )


@pytest.mark.asyncio
async def test_variant_manager_registers_variant(tmp_path: Path):
    """Manager registers a new variant and returns a variant_id."""
    registry = JSONRegistry(tmp_path / "registry.json")
    enforcer = BudgetEnforcer(max_total=10, max_per_session=5)
    manager = VariantManager(registry, enforcer)

    result = await manager.register(_make_variant(), _make_comparison(), user_id="user-1")

    assert result.variant_id
    assert not result.is_duplicate


@pytest.mark.asyncio
async def test_variant_manager_enforces_budget(tmp_path: Path):
    """Manager raises VariantBudgetExceededError when budget is exhausted."""
    registry = JSONRegistry(tmp_path / "registry.json")
    enforcer = BudgetEnforcer(max_total=1, max_per_session=1)
    manager = VariantManager(registry, enforcer)

    await manager.register(_make_variant("job-001"), _make_comparison(), user_id="user-1")

    with pytest.raises(VariantBudgetExceededError):
        await manager.register(_make_variant("job-002"), _make_comparison(), user_id="user-1")


@pytest.mark.asyncio
async def test_variant_manager_detects_duplicate(tmp_path: Path):
    """Manager raises ValidationError on duplicate job variant."""
    registry = JSONRegistry(tmp_path / "registry.json")
    enforcer = BudgetEnforcer(max_total=10, max_per_session=5)
    manager = VariantManager(registry, enforcer)

    await manager.register(_make_variant("job-001"), _make_comparison(), user_id="user-1")

    with pytest.raises(ValidationError):
        await manager.register(_make_variant("job-001"), _make_comparison(), user_id="user-1")
