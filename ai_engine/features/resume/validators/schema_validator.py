"""Schema validator for parsed resume data."""

from __future__ import annotations

from ai_engine.core.exceptions import SchemaValidationError
from ai_engine.features.resume.models.resume_schema import ResumeData


def validate_resume_schema(data: ResumeData) -> None:
    """Validate that a parsed ResumeData meets minimum quality requirements.

    Args:
        data: Parsed ResumeData instance.

    Raises:
        SchemaValidationError: If required fields are missing or malformed.
    """
    if not data.personal.name and not data.personal.email:
        raise SchemaValidationError(
            "Resume must have at least a name or email in personal info.",
            field="personal",
        )

    if not data.skills and not data.experience_entries:
        raise SchemaValidationError(
            "Resume must have at least skills or experience entries.",
            field="skills/experience_entries",
        )

    for idx, entry in enumerate(data.experience_entries):
        if not entry.company and not entry.role:
            raise SchemaValidationError(
                f"Experience entry {idx} is missing both company and role.",
                field=f"experience_entries[{idx}]",
            )
