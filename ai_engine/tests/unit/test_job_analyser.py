"""Unit tests for job analyser."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.features.analysis.job_analyser import JobAnalyser
from ai_engine.features.analysis.strategies.llm_analyzer import LLMAnalyzerStrategy
from ai_engine.features.llm.base import LLMResult
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry
from ai_engine.tests.fixtures.sample_jobs import SAMPLE_JOB_CLEAR


def _make_strategy(response_content: dict, prompts_dir: Path) -> LLMAnalyzerStrategy:
    router = MagicMock()
    router.complete = AsyncMock(
        return_value=LLMResult(content=response_content, provider="mock", model="mock")
    )
    loader = PromptLoader(prompts_dir)
    registry = PromptRegistry(prompts_dir)
    return LLMAnalyzerStrategy(router, loader, registry)


@pytest.mark.asyncio
async def test_job_analyser_returns_analysis(prompts_dir: Path):
    """Analyser returns JobAnalysis when LLM returns valid response."""
    response = {
        "required_skills": ["Python", "PostgreSQL"],
        "preferred_skills": ["AWS"],
        "experience_level": "senior",
        "role_clarity_score": 4,
        "key_responsibilities": ["Build APIs"],
        "implied_values": ["quality"],
        "red_flag_signals": [],
        "application_tone": "formal",
    }
    strategy = _make_strategy(response, prompts_dir)
    analyser = JobAnalyser(strategy)

    analysis = await analyser.analyse(SAMPLE_JOB_CLEAR)

    assert analysis.experience_level == "senior"
    assert "Python" in analysis.required_skills


@pytest.mark.asyncio
async def test_job_analyser_raises_on_invalid_schema(prompts_dir: Path):
    """Analyser raises SchemaValidationError when LLM returns invalid data."""
    strategy = _make_strategy({"role_clarity_score": 99}, prompts_dir)  # Invalid score
    analyser = JobAnalyser(strategy)

    with pytest.raises(SchemaValidationError):
        await analyser.analyse(SAMPLE_JOB_CLEAR)
