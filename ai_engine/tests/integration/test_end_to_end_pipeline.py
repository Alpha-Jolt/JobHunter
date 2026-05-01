"""Integration test: end-to-end pipeline (generate mode)."""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.features.llm.base import LLMResult
from ai_engine.features.llm.prompting.prompt_loader import PromptLoader
from ai_engine.features.llm.prompting.registry import PromptRegistry


def _make_router(prompts_dir: Path) -> MagicMock:
    """Build a mock router that returns valid responses for all LLM calls."""
    analysis_response = {
        "required_skills": ["Python", "PostgreSQL"],
        "preferred_skills": ["AWS"],
        "experience_level": "senior",
        "role_clarity_score": 4,
        "key_responsibilities": ["Build APIs", "Mentor team"],
        "implied_values": ["quality"],
        "red_flag_signals": [],
        "application_tone": "formal",
    }
    comparison_response = {
        "match_score": 78,
        "matched_skills": ["Python", "PostgreSQL"],
        "gap_skills": ["AWS"],
        "matched_experience": ["Senior Developer at TechCorp"],
        "weak_points": [],
        "strength_summary": "Strong Python background.",
    }
    optimiser_response = {
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
        "gaps": ["AWS"],
    }

    call_count = 0
    responses = [analysis_response, comparison_response, optimiser_response]

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        resp = responses[call_count % len(responses)]
        call_count += 1
        return LLMResult(content=resp, provider="mock", model="mock")

    router = MagicMock()
    router.complete = AsyncMock(side_effect=side_effect)
    return router


@pytest.mark.asyncio
async def test_end_to_end_generate_mode(tmp_path: Path, prompts_dir: Path):
    """Generate mode: scraper CSV → parse resume → analyse → compare
    → optimise → register variant."""
    Document = pytest.importorskip("docx", reason="python-docx not installed").Document

    from ai_engine.features.analysis.job_analyser import JobAnalyser
    from ai_engine.features.analysis.strategies.llm_analyzer import LLMAnalyzerStrategy
    from ai_engine.features.matching.comparator import Comparator
    from ai_engine.features.matching.strategies.llm_comparison import LLMComparisonStrategy
    from ai_engine.features.optimization.resume_optimiser import ResumeOptimiser
    from ai_engine.features.optimization.strategies.llm_optimiser_strategy import (
        LLMOptimiserStrategy,
    )
    from ai_engine.features.orchestration.modes.generate_mode import run_generate_mode
    from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
    from ai_engine.core.types import PipelineMode
    from ai_engine.features.resume.resume_parser import ResumeParser
    from ai_engine.features.resume.strategies.llm_parser_strategy import LLMParserStrategy
    from ai_engine.features.variant_management.limiters.budget_enforcer import BudgetEnforcer
    from ai_engine.features.variant_management.manager import VariantManager
    from ai_engine.features.variant_management.registries.json_registry import JSONRegistry

    # Create scraper output CSV
    scraper_dir = tmp_path / "output" / "final"
    scraper_dir.mkdir(parents=True)
    csv_path = scraper_dir / "jobs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["job_id", "source", "title", "company", "description", "apply_url"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "job_id": "j-e2e-001",
                "source": "indeed",
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "description": (
                    "Senior Python Developer needed with PostgreSQL, Docker, REST APIs. "
                    "5+ years experience. Build scalable backend services."
                ),
                "apply_url": "https://techcorp.com/jobs/1",
            }
        )

    # Create resume DOCX
    resume_path = tmp_path / "resume.docx"
    doc = Document()
    doc.add_paragraph("John Doe")
    doc.add_paragraph("john@example.com")
    doc.add_paragraph("SKILLS")
    doc.add_paragraph("Python, PostgreSQL, Docker, FastAPI, REST APIs, Git")
    doc.add_paragraph("EXPERIENCE")
    doc.add_paragraph("Senior Developer at TechCorp (2020-2024)")
    doc.add_paragraph("Built REST APIs using Python and FastAPI")
    doc.add_paragraph("Managed PostgreSQL databases")
    doc.save(str(resume_path))

    # Wire up components
    router = _make_router(prompts_dir)
    loader = PromptLoader(prompts_dir)
    registry_obj = PromptRegistry(prompts_dir)

    # Parser needs its own router call sequence — reset
    parse_response = {
        "personal": {"name": "John Doe", "email": "john@example.com"},
        "summary": "Experienced Python developer with 6 years building backend systems.",
        "experience_entries": [
            {
                "company": "TechCorp",
                "role": "Senior Developer",
                "duration": "2020-2024",
                "responsibilities": ["Built REST APIs using Python and FastAPI"],
                "achievements": ["Managed PostgreSQL databases"],
            }
        ],
        "education": [],
        "skills": ["Python", "PostgreSQL", "Docker", "FastAPI", "REST APIs", "Git"],
        "certifications": [],
        "projects": [],
    }
    parse_router = MagicMock()
    parse_router.complete = AsyncMock(
        return_value=LLMResult(content=parse_response, provider="mock", model="mock")
    )

    resume_parser = ResumeParser(LLMParserStrategy(parse_router, loader, registry_obj))
    job_analyser = JobAnalyser(LLMAnalyzerStrategy(router, loader, registry_obj))
    comparator = Comparator(LLMComparisonStrategy(router, loader, registry_obj))
    optimiser = ResumeOptimiser(LLMOptimiserStrategy(router, loader, registry_obj))

    json_registry = JSONRegistry(tmp_path / "registry.json")
    budget = BudgetEnforcer(max_total=10, max_per_session=10)
    variant_manager = VariantManager(json_registry, budget)

    config = PipelineConfig(
        scraper_output_dir=scraper_dir,
        ai_output_dir=tmp_path / "ai_output",
        resume_file_path=resume_path,
        user_id="user-test",
        session_id="session-e2e",
        mode=PipelineMode.GENERATE,
    )

    result = await run_generate_mode(
        config=config,
        resume_parser=resume_parser,
        job_analyser=job_analyser,
        comparator=comparator,
        optimiser=optimiser,
        variant_manager=variant_manager,
    )

    assert result.status in ("success", "partial_failure")
    assert result.generated_variants >= 1
    assert len(result.variant_ids) >= 1
