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
    from ai_engine.features.orchestration.modes.release_mode import (
        run_release_mode,
    )
    from ai_engine.core.config import get_settings
    from ai_engine.features.orchestration.builder import PipelineBuilder

    registry = JSONRegistry(tmp_path / "registry.json")
    await registry.save(
        VariantRecord(
            variant_id="v-pending",
            job_id="job-001",
            user_id="user-1",
            approval_status=ApprovalStatus.PENDING,
        )
    )

    mock_router = MagicMock()
    mock_router.complete = AsyncMock(
        return_value=LLMResult(
            content={"cover_letter_text": "Dear Hiring Manager...", "word_count": 3},
            provider="mock",
            model="mock",
        )
    )

    settings = get_settings()
    settings.paths.prompts_dir = prompts_dir
    settings.paths.output_dir = tmp_path / "output"

    from unittest.mock import patch
    with patch("ai_engine.features.orchestration.builder.LLMRouter", return_value=mock_router):
        builder = PipelineBuilder(settings)
        pipeline = builder.build(variant_registry=registry)

    result = await run_release_mode(
        variant_jobs=[("v-pending", _make_variant(), SAMPLE_JOB_ANALYSIS, SAMPLE_JOB_CLEAR)],
        output_builder=pipeline._executor._output_builder,
    )

    assert result.output_packages == 0
    assert len(result.errors) == 1
    assert "not approved" in result.errors[0]
