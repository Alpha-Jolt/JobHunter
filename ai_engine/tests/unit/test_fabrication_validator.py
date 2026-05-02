"""Unit tests for fabrication validator."""

from __future__ import annotations

from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.optimization.validators.fabrication_validator import validate_variant
from ai_engine.features.resume.models.resume_schema import ExperienceEntry
from ai_engine.tests.fixtures.sample_resumes import SAMPLE_RESUME


def test_fabrication_validator_passes_clean_variant():
    """Validator passes when all variant content exists in source resume."""
    variant = OptimisedVariant(
        reordered_experience=list(SAMPLE_RESUME.experience_entries),
        rewritten_summary=SAMPLE_RESUME.summary,
        prioritized_skills=list(SAMPLE_RESUME.skills),
        selected_projects=[],
        selected_certifications=[],
        gaps=["Kubernetes"],
        job_id="job-001",
    )
    result = validate_variant(variant, SAMPLE_RESUME)
    assert result.passed


def test_fabrication_validator_rejects_invented_skill():
    """Validator rejects a variant containing a skill not in the source resume."""
    variant = OptimisedVariant(
        reordered_experience=list(SAMPLE_RESUME.experience_entries),
        rewritten_summary=SAMPLE_RESUME.summary,
        prioritized_skills=["Python", "QuantumComputing"],  # QuantumComputing is fabricated
        selected_projects=[],
        selected_certifications=[],
        gaps=[],
        job_id="job-001",
    )
    result = validate_variant(variant, SAMPLE_RESUME)
    assert not result.passed
    assert any("QuantumComputing" in item for item in result.fabricated_items)


def test_fabrication_validator_rejects_invented_company():
    """Validator rejects a variant with a fabricated company name."""
    fake_entry = ExperienceEntry(
        company="FakeCompanyXYZ",
        role="Senior Developer",
        duration="2020-2024",
        responsibilities=["Built APIs"],
        achievements=[],
    )
    variant = OptimisedVariant(
        reordered_experience=[fake_entry],
        rewritten_summary="",
        prioritized_skills=list(SAMPLE_RESUME.skills),
        selected_projects=[],
        selected_certifications=[],
        gaps=[],
        job_id="job-001",
    )
    result = validate_variant(variant, SAMPLE_RESUME)
    assert not result.passed
