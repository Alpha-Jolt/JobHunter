"""Fabrication validator — deterministic anti-fabrication gate for optimised variants.

This is a set operation, never an LLM call.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.resume.models.resume_schema import ResumeData
from ai_engine.shared.text_utils import normalise_for_comparison


@dataclass
class FabricationValidationResult:
    """Result of the fabrication validation gate.

    Attributes:
        passed: True if no fabricated content was found.
        fabricated_items: List of items that were not in the source resume.
    """

    passed: bool
    fabricated_items: list[str] = field(default_factory=list)


def _build_source_set(resume: ResumeData) -> set[str]:
    """Build a normalised token set from all resume content.

    Args:
        resume: Source ResumeData.

    Returns:
        Set of normalised tokens from all resume fields.
    """
    parts: list[str] = [resume.raw_text, resume.summary]
    parts.extend(resume.skills)
    parts.extend(resume.certifications)
    for entry in resume.experience_entries:
        parts.extend([entry.company, entry.role, entry.duration])
        parts.extend(entry.responsibilities)
        parts.extend(entry.achievements)
    for proj in resume.projects:
        parts.extend([proj.name, proj.description])
        parts.extend(proj.technologies)

    combined = " ".join(p for p in parts if p)
    return set(normalise_for_comparison(combined).split())


def _value_in_source(value: str, source_tokens: set[str]) -> bool:
    """Check if a value's significant tokens are present in the source.

    Args:
        value: Value to check.
        source_tokens: Normalised token set from source resume.

    Returns:
        True if the value is sufficiently present.
    """
    tokens = {t for t in normalise_for_comparison(value).split() if len(t) > 2}
    if not tokens:
        return True
    overlap = tokens & source_tokens
    return len(overlap) / len(tokens) >= 0.6


def validate_variant(
    variant: OptimisedVariant, source_resume: ResumeData
) -> FabricationValidationResult:
    """Validate that all content in the variant exists in the source resume.

    Checks: prioritized_skills, selected_certifications, experience roles/companies.

    Args:
        variant: The OptimisedVariant to validate.
        source_resume: The original ResumeData (immutable source of truth).

    Returns:
        FabricationValidationResult with pass/fail and fabricated items.
    """
    source_tokens = _build_source_set(source_resume)
    fabricated: list[str] = []

    for skill in variant.prioritized_skills:
        if not _value_in_source(skill, source_tokens):
            fabricated.append(f"skill: '{skill}'")

    for cert in variant.selected_certifications:
        if not _value_in_source(cert, source_tokens):
            fabricated.append(f"certification: '{cert}'")

    for entry in variant.reordered_experience:
        for field_name in ("company", "role"):
            value = getattr(entry, field_name, "")
            if value and not _value_in_source(value, source_tokens):
                fabricated.append(f"experience.{field_name}: '{value}'")

    return FabricationValidationResult(passed=len(fabricated) == 0, fabricated_items=fabricated)
