"""Template validator — validates email and resume template formats."""

from __future__ import annotations

import re
from pathlib import Path

from ai_engine.core.exceptions import ValidationError

_REQUIRED_EMAIL_SLOTS = {"job_title", "company"}


def validate_email_template(template_text: str) -> None:
    """Validate that an email template contains required variable slots.

    Args:
        template_text: Raw email template string.

    Raises:
        ValidationError: If required slots are missing.
    """
    found_slots = set(re.findall(r"\$\{?(\w+)\}?", template_text))
    missing = _REQUIRED_EMAIL_SLOTS - found_slots
    if missing:
        raise ValidationError(
            f"Email template is missing required slots: {missing}. " f"Found slots: {found_slots}"
        )


def validate_resume_template(template_path: Path) -> None:
    """Validate that a resume template is a valid DOCX file.

    Args:
        template_path: Path to the DOCX template.

    Raises:
        ValidationError: If the file is not a valid DOCX.
    """
    if not template_path.exists():
        raise ValidationError(f"Resume template not found: {template_path}")
    if template_path.suffix.lower() not in (".docx", ".doc"):
        raise ValidationError(f"Resume template must be a DOCX file: {template_path}")
    # Basic DOCX magic bytes check (PK zip header)
    with template_path.open("rb") as fh:
        header = fh.read(4)
    if header[:2] != b"PK":
        raise ValidationError(
            f"Resume template does not appear to be a valid DOCX (ZIP) file: {template_path}"
        )
