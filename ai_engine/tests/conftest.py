"""Shared pytest fixtures for the AI Engine test suite."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.features.llm.base import LLMResult


@pytest.fixture
def sample_job_description() -> str:
    return (
        "We are looking for a Senior Python Developer with 5+ years of experience. "
        "Required skills: Python, PostgreSQL, Docker, REST APIs. "
        "Preferred: Kubernetes, AWS. "
        "Responsibilities: Build scalable backend services, mentor junior developers."
    )


@pytest.fixture
def sample_resume_text() -> str:
    return (
        "John Doe\njohn@example.com | +1-555-0100\n\n"
        "SUMMARY\nExperienced Python developer with 6 years building backend systems.\n\n"
        "EXPERIENCE\nSenior Developer at TechCorp (2020-2024)\n"
        "- Built REST APIs using Python and FastAPI\n"
        "- Managed PostgreSQL databases\n"
        "- Deployed services with Docker\n\n"
        "SKILLS\nPython, PostgreSQL, Docker, FastAPI, REST APIs, Git\n\n"
        "EDUCATION\nB.Sc. Computer Science, State University, 2018"
    )


@pytest.fixture
def mock_llm_result() -> LLMResult:
    return LLMResult(
        content={},
        provider="mock",
        model="mock-model",
        prompt_tokens=100,
        completion_tokens=200,
        latency_seconds=0.5,
    )


@pytest.fixture
def mock_router(mock_llm_result: LLMResult):
    """Mock LLMRouter that returns a configurable result."""
    router = MagicMock()
    router.complete = AsyncMock(return_value=mock_llm_result)
    return router


@pytest.fixture
def prompts_dir(tmp_path: Path) -> Path:
    """Create a temporary prompts directory with all required prompt files."""
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    for name in [
        "job_analyser_v1",
        "resume_parser_v1",
        "comparison_engine_v1",
        "resume_optimiser_v1",
        "cover_letter_v1",
    ]:
        (prompts / f"{name}.txt").write_text(
            f"Test prompt for {name}. Job: $job_description", encoding="utf-8"
        )
    return prompts
