"""Unit tests for resume optimiser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.core.exceptions import FabricationDetectedError
from ai_engine.features.llm.base import LLMResult
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.matching.models.comparison_result import ComparisonResult
from ai_engine.features.optimization.resume_optimiser import ResumeOptimiser
from ai_engine.features.optimization.strategies.llm_optimiser_strategy import LLMOptimiserStrategy
from ai_engine.tests.fixtures.sample_analyses import SAMPLE_JOB_ANALYSIS
from ai_engine.tests.fixtures.sample_resumes import SAMPLE_RESUME


def _make_optimiser(response_content: dict, prompts_dir: Path) -> ResumeOptimiser:
    router = MagicMock()
    router.complete = AsyncMock(
        return_value=LLMResult(content=response_content, provider="mock", model="mock")
    )
    strategy = LLMOptimiserStrategy(router, PromptLoader(prompts_dir), PromptRegistry(prompts_dir))
    return ResumeOptimiser(strategy)


def _make_comparison() -> ComparisonResult:
    return ComparisonResult(
        match_score=80,
        matched_skills=["Python", "PostgreSQL"],
        gap_skills=["Kubernetes"],
        job_id="job-001",
    )


@pytest.mark.asyncio
async def test_optimiser_returns_valid_variant(prompts_dir: Path):
    """Optimiser returns OptimisedVariant when LLM returns valid content."""
    response = {
        "reordered_experience": [
            {
                "company": "TechCorp",
                "role": "Senior Developer",
                "duration": "2020-2024",
                "responsibilities": ["Built REST APIs using Python"],
                "achievements": [],
            }
        ],
        "rewritten_summary": "Experienced Python developer with 6 years building backend systems.",
        "prioritized_skills": ["Python", "PostgreSQL", "Docker"],
        "selected_projects": [],
        "selected_certifications": [],
        "gaps": ["Kubernetes"],
    }
    optimiser = _make_optimiser(response, prompts_dir)
    variant = await optimiser.optimise(SAMPLE_RESUME, SAMPLE_JOB_ANALYSIS, _make_comparison())

    assert "Python" in variant.prioritized_skills
    assert "Kubernetes" in variant.gaps


@pytest.mark.asyncio
async def test_optimiser_rejects_fabricated_skill(prompts_dir: Path):
    """Optimiser raises FabricationDetectedError when LLM invents a skill."""
    response = {
        "reordered_experience": [],
        "rewritten_summary": "",
        "prioritized_skills": ["Python", "QuantumNeuralNetworkXYZ"],  # Fabricated
        "selected_projects": [],
        "selected_certifications": [],
        "gaps": [],
    }
    optimiser = _make_optimiser(response, prompts_dir)

    with pytest.raises(FabricationDetectedError):
        await optimiser.optimise(SAMPLE_RESUME, SAMPLE_JOB_ANALYSIS, _make_comparison())
