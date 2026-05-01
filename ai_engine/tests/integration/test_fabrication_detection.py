"""Integration test: fabrication detection end-to-end."""

from __future__ import annotations

from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.optimization.validators.fabrication_validator import validate_variant
from ai_engine.tests.fixtures.sample_resumes import SAMPLE_RESUME


def test_fabrication_detection_catches_injected_skill():
    """Injecting a fake skill into a variant is caught by the validator."""
    variant = OptimisedVariant(
        reordered_experience=list(SAMPLE_RESUME.experience_entries),
        rewritten_summary=SAMPLE_RESUME.summary,
        prioritized_skills=["Python", "BlockchainAIQuantumXYZ"],  # Injected fake
        selected_projects=[],
        selected_certifications=[],
        gaps=[],
        job_id="job-001",
    )
    result = validate_variant(variant, SAMPLE_RESUME)
    assert not result.passed
    assert len(result.fabricated_items) > 0


def test_fabrication_detection_passes_real_content():
    """Validator passes when all content is from the source resume."""
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
