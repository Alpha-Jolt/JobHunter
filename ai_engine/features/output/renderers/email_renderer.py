"""Email renderer — fills user-provided template slots with structured data."""

from __future__ import annotations

from pathlib import Path
from string import Template

from ai_engine.core.exceptions import OutputRenderError
from ai_engine.core.logging_.logger import get_logger

logger = get_logger(__name__)


async def render_email(
    template_path: Path,
    variables: dict[str, str],
    output_dir: Path,
    job_id: str,
) -> str:
    """Fill an email template with structured data and write to disk.

    Does NOT generate email content — only fills provided template slots.
    Missing slots are left as-is (safe_substitute behaviour).

    Args:
        template_path: Path to the user's email template file.
        variables: Dict of slot name → value mappings.
        output_dir: Directory to write the rendered email draft.
        job_id: Job identifier for file naming.

    Returns:
        Path to the rendered email draft file.

    Raises:
        OutputRenderError: If template file cannot be read.
    """
    if not template_path.exists():
        raise OutputRenderError(f"Email template not found: {template_path}")

    raw_template = template_path.read_text(encoding="utf-8")
    rendered = Template(raw_template).safe_substitute(variables)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"email_draft_{job_id}.txt"
    output_path.write_text(rendered, encoding="utf-8")

    logger.info("email_renderer.written", path=str(output_path))
    return str(output_path)
