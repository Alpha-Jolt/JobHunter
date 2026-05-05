"""Unit tests for comparator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.features.llm.base import LLMResult
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.features.matching.comparator import Comparator
from ai_engine.features.matching.strategies.llm_comparison import LLMComparisonStrategy
from ai_engine.tests.fixtures.sample_analyses import SAMPLE_JOB_ANALYSIS
from ai_engine.tests.fixtures.sample_resumes import SAMPLE_RESUME


@pytest.mark.asyncio
async def test_comparator_returns_result(prompts_dir: Path):
    """Comparator returns ComparisonResult with match score."""
    response = {
        "match_score": 80,
        "matched_skills": ["Python", "PostgreSQL"],
        "gap_skills": ["Kubernetes"],
        "matched_experience": ["Senior Developer at TechCorp"],
        "weak_points": [],
        "strength_summary": "Strong Python and PostgreSQL background.",
    }
    router = MagicMock()
    router.complete = AsyncMock(
        return_value=LLMResult(content=response, provider="mock", model="mock")
    )
    strategy = LLMComparisonStrategy(router, PromptLoader(prompts_dir), PromptRegistry(prompts_dir))
    comparator = Comparator(strategy)

    result = await comparator.compare(SAMPLE_RESUME, SAMPLE_JOB_ANALYSIS)

    assert result.match_score == 80
    assert "Python" in result.matched_skills
    assert "Kubernetes" in result.gap_skills
