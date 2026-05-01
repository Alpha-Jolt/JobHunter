"""Integration test: output file generation (release mode)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.core.types import ApprovalStatus
from ai_engine.features.approval.approval_gate import ApprovalGate
from ai_engine.features.llm.base import LLMResult
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.variant_management.models.variant_record import VariantRecord
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry
from ai_engine.tests.fixtures.sample_analyses import SAMPLE_JOB_ANALYSIS
from ai_engine.tests.fixtures.sample_jobs import SAMPLE_JOB_CLEAR


def _make_variant(job_id: str = "job-001") -> OptimisedVariant:
    return OptimisedVariant(
        reordered_experience=[],
        rewritten_summary="Experienced Python developer.",
        prioritized_skills=["Python", "Docker"],
        selected_projects=[],
        selected_certifications=[],
        gaps=["Kubernetes"],
        job_id=job_id,
    )


@pytest.mark.asyncio
async def test_release_mode_skips_unapproved(tmp_path: Path, prompts_dir: Path):
    """Release mode skips unapproved variants and reports them as errors."""
    from ai_engine.features.llm.prompting.prompt_loader import PromptLoader  # noqa: PLC0415
    from ai_engine.features.llm.prompting.registry import PromptRegistry  # noqa: PLC0415
    from ai_engine.features.orchestration.modes.release_mode import (
        run_release_mode,
    )  # noqa: PLC0415
    from ai_engine.features.output.output_builder import OutputBuilder  # noqa: PLC0415
    from ai_engine.features.output.strategies.llm_cover_letter_strategy import (  # noqa: PLC0415
        LLMCoverLetterStrategy,
    )

    registry = JSONRegistry(tmp_path / "registry.json")
    registry.create(
        VariantRecord(
            variant_id="v-pending",
            job_id="job-001",
            user_id="user-1",
            approval_status=ApprovalStatus.PENDING,
        )
    )

    gate = ApprovalGate(registry)
    mock_router = MagicMock()
    mock_router.complete = AsyncMock(
        return_value=LLMResult(
            content={"cover_letter_text": "Dear Hiring Manager...", "word_count": 3},
            provider="mock",
            model="mock",
        )
    )
    cover_strategy = LLMCoverLetterStrategy(
        mock_router, PromptLoader(prompts_dir), PromptRegistry(prompts_dir)
    )
    builder = OutputBuilder(gate, cover_strategy, tmp_path / "output")

    result = await run_release_mode(
        variant_jobs=[("v-pending", _make_variant(), SAMPLE_JOB_ANALYSIS, SAMPLE_JOB_CLEAR)],
        output_builder=builder,
    )

    assert result.output_packages == 0
    assert len(result.errors) == 1
    assert "not approved" in result.errors[0]
