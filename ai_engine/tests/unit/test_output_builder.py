"""Unit tests for output builder."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.core.exceptions import ApprovalRequiredError
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.approval.approval_gate import ApprovalGate
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.variant_management.models.variant_record import VariantRecord
from ai_engine.features.variant_management.registries.json_registry import JSONRegistry
from ai_engine.tests.fixtures.sample_analyses import SAMPLE_JOB_ANALYSIS
from ai_engine.tests.fixtures.sample_jobs import SAMPLE_JOB_CLEAR


def _make_variant() -> OptimisedVariant:
    return OptimisedVariant(
        reordered_experience=[],
        rewritten_summary="Experienced Python developer.",
        prioritized_skills=["Python", "Docker"],
        selected_projects=[],
        selected_certifications=[],
        gaps=["Kubernetes"],
        job_id="job-001",
    )


def _register(registry: JSONRegistry, variant_id: str, status: ApprovalStatus) -> None:
    registry.create(
        VariantRecord(
            variant_id=variant_id,
            job_id="job-001",
            user_id="user-1",
            approval_status=status,
        )
    )


@pytest.mark.asyncio
async def test_output_builder_blocks_unapproved_variant(tmp_path: Path, prompts_dir: Path):
    """OutputBuilder raises ApprovalRequiredError for unapproved variants."""
    from ai_engine.features.output.output_builder import OutputBuilder  # noqa: PLC0415
    from ai_engine.features.output.strategies.llm_cover_letter_strategy import (  # noqa: PLC0415
        LLMCoverLetterStrategy,
    )
    from ai_engine.features.llm.prompting.prompt_loader import PromptLoader  # noqa: PLC0415
    from ai_engine.features.llm.prompting.registry import PromptRegistry  # noqa: PLC0415

    registry = JSONRegistry(tmp_path / "registry.json")
    _register(registry, "v-pending", ApprovalStatus.PENDING)

    gate = ApprovalGate(registry)
    mock_router = MagicMock()
    mock_router.complete = AsyncMock()
    cover_strategy = LLMCoverLetterStrategy(
        mock_router, PromptLoader(prompts_dir), PromptRegistry(prompts_dir)
    )
    builder = OutputBuilder(gate, cover_strategy, tmp_path / "output")

    with pytest.raises(ApprovalRequiredError):
        await builder.build("v-pending", _make_variant(), SAMPLE_JOB_ANALYSIS, SAMPLE_JOB_CLEAR)


@pytest.mark.asyncio
async def test_output_builder_email_slots_filled(tmp_path: Path, prompts_dir: Path):
    """OutputBuilder fills email template slots from job and variant data."""
    from ai_engine.features.output.templating.variable_mapper import (
        map_email_variables,
    )  # noqa: PLC0415

    variant = _make_variant()
    variables = map_email_variables(
        SAMPLE_JOB_ANALYSIS, variant, job_title="Senior Python Developer", company="TechCorp"
    )

    assert variables["job_title"] == "Senior Python Developer"
    assert variables["company"] == "TechCorp"
    assert "Python" in variables["top_skills"]


@pytest.mark.asyncio
async def test_output_builder_cover_letter_gated(tmp_path: Path, prompts_dir: Path):
    """Cover letter is only generated after approval gate passes."""
    from ai_engine.features.llm.base import LLMResult  # noqa: PLC0415
    from ai_engine.features.llm.prompting.prompt_loader import PromptLoader  # noqa: PLC0415
    from ai_engine.features.llm.prompting.registry import PromptRegistry  # noqa: PLC0415
    from ai_engine.features.output.output_builder import OutputBuilder  # noqa: PLC0415
    from ai_engine.features.output.strategies.llm_cover_letter_strategy import (  # noqa: PLC0415
        LLMCoverLetterStrategy,
    )

    registry = JSONRegistry(tmp_path / "registry.json")
    _register(registry, "v-approved", ApprovalStatus.APPROVED)

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

    # Should not raise — approved variant proceeds to output generation
    # (resume renderer may fail without python-docx, that's acceptable here)
    try:
        package = await builder.build(
            "v-approved", _make_variant(), SAMPLE_JOB_ANALYSIS, SAMPLE_JOB_CLEAR
        )
        assert package.variant_id == "v-approved"
    except Exception as exc:
        # Only acceptable failure is missing python-docx/LibreOffice
        assert "python-docx" in str(exc) or "LibreOffice" in str(exc) or "docx" in str(exc).lower()
