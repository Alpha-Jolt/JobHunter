"""Template loader — loads and validates user email and resume templates."""

from __future__ import annotations

from pathlib import Path

from ai_engine.core.exceptions import OutputRenderError


def load_email_template(template_path: Path) -> str:
    """Load and return the raw email template text.

    Args:
        template_path: Path to the email template file.

    Returns:
        Raw template string.

    Raises:
        OutputRenderError: If file does not exist or cannot be read.
    """
    if not template_path.exists():
        raise OutputRenderError(f"Email template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def load_resume_template(template_path: Path) -> Path:
    """Validate and return the resume DOCX template path.

    Args:
        template_path: Path to the DOCX template file.

    Returns:
        Validated template path.

    Raises:
        OutputRenderError: If file does not exist or is not a DOCX.
    """
    if not template_path.exists():
        raise OutputRenderError(f"Resume template not found: {template_path}")
    if template_path.suffix.lower() not in (".docx", ".doc"):
        raise OutputRenderError(f"Resume template must be a DOCX file: {template_path}")
    return template_path
