"""Integration test: end-to-end pipeline (generate mode)."""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.features.llm.base import LLMResult
from ai_engine.core.config import get_settings
from ai_engine.features.orchestration.builder import PipelineBuilder


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

    call_count = 0
    responses = [parse_response, analysis_response, comparison_response, optimiser_response]

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        resp = responses[call_count % len(responses)]
        call_count += 1
        return LLMResult(content=resp, provider="mock", model="mock")

    mock_router = MagicMock()
    mock_router.complete = AsyncMock(side_effect=side_effect)
    return mock_router


@pytest.mark.asyncio
async def test_end_to_end_generate_mode(tmp_path: Path, prompts_dir: Path):
    """Generate mode: scraper CSV → parse resume → analyse → compare
    → optimise → register variant."""
    Document = pytest.importorskip("docx", reason="python-docx not installed").Document

    from ai_engine.features.orchestration.modes.generate_mode import run_generate_mode
    from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
    from ai_engine.core.types import PipelineMode
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

    router = _make_router(prompts_dir)
    json_registry = JSONRegistry(tmp_path / "registry.json")
    
    settings = get_settings()
    settings.paths.prompts_dir = prompts_dir
    settings.max_variants_total = 2
    settings.max_variants_per_session = 2
    
    with patch("ai_engine.features.orchestration.builder.LLMRouter", return_value=router):
        builder = PipelineBuilder(settings)
        pipeline = builder.build(variant_registry=json_registry)

    config = PipelineConfig(
        session_id="e2e-session-001",
        user_id="user-001",
        mode=PipelineMode.GENERATE,
        scraper_output_dir=scraper_dir,
        resume_file_path=resume_path,
        auto_approve=False,
    )

    result = await run_generate_mode(
        config=config,
        resume_parser=pipeline._executor._resume_parser,
        job_analyser=pipeline._executor._job_analyser,
        comparator=pipeline._executor._comparator,
        optimiser=pipeline._executor._optimiser,
        variant_manager=pipeline._executor._variant_manager,
    )

    assert result.status in ("success", "partial_failure")
    assert result.generated_variants >= 1
    assert len(result.variant_ids) >= 1
