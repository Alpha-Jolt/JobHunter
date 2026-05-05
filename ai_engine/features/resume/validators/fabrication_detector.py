"""Fabrication detector — deterministic post-parse cross-validation.

This is a set operation, never an LLM call.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_engine.shared.text_utils import normalise_for_comparison


@dataclass
class FabricationReport:
    """Result of a fabrication detection check.

    Attributes:
        is_clean: True if no fabricated fields were found.
        fabricated_fields: List of field names with fabricated content.
        details: Human-readable detail per fabricated field.
    """

    is_clean: bool
    fabricated_fields: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)


def _build_source_tokens(raw_text: str) -> set[str]:
    """Build a set of normalised tokens from the source text.

    Args:
        raw_text: Original extracted resume text.

    Returns:
        Set of normalised word tokens.
    """
    normalised = normalise_for_comparison(raw_text)
    return set(normalised.split())


def _is_present_in_source(value: str, source_tokens: set[str]) -> bool:
    """Check if all significant words of a value appear in the source tokens.

    A value is considered present if at least 60% of its words (min 1) appear
    in the source. This handles minor rephrasing while catching outright fabrication.

    Args:
        value: The value to check.
        source_tokens: Normalised token set from source text.

    Returns:
        True if the value is sufficiently present in the source.
    """
    value_tokens = set(normalise_for_comparison(value).split())
    # Filter out very short tokens (articles, prepositions)
    significant = {t for t in value_tokens if len(t) > 2}
    if not significant:
        return True  # Nothing meaningful to check
    overlap = significant & source_tokens
    return len(overlap) / len(significant) >= 0.6


def detect_fabrication(resume_data: object, raw_text: str) -> FabricationReport:
    """Cross-validate parsed resume fields against the source text.

    Checks skills, certifications, and experience roles/companies.
    This is a deterministic set operation — no LLM involved.

    Args:
        resume_data: ResumeData instance to validate.
        raw_text: Original extracted text (resume_data.raw_text).

    Returns:
        FabricationReport indicating clean or fabricated fields.
    """
    source_tokens = _build_source_tokens(raw_text)
    fabricated_fields: list[str] = []
    details: list[str] = []

    # Check skills
    for skill in getattr(resume_data, "skills", []):
        if not _is_present_in_source(skill, source_tokens):
            fabricated_fields.append("skills")
            details.append(f"Skill not found in source: '{skill}'")

    # Check certifications
    for cert in getattr(resume_data, "certifications", []):
        if not _is_present_in_source(cert, source_tokens):
            fabricated_fields.append("certifications")
            details.append(f"Certification not found in source: '{cert}'")

    # Check experience entries
    for idx, entry in enumerate(getattr(resume_data, "experience_entries", [])):
        for field_name in ("company", "role"):
            value = getattr(entry, field_name, "")
            if value and not _is_present_in_source(value, source_tokens):
                fabricated_fields.append(f"experience_entries[{idx}].{field_name}")
                details.append(f"Experience {field_name} not found in source: '{value}'")

    is_clean = len(fabricated_fields) == 0
    return FabricationReport(
        is_clean=is_clean, fabricated_fields=fabricated_fields, details=details
    )
