"""Cover letter renderer — generates PDF cover letter via LLM + LibreOffice."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engine.core.exceptions import OutputRenderError
from ai_engine.core.logging_.logger import get_logger

logger = get_logger(__name__)


def _write_text_to_pdf(text: str, output_path: Path) -> None:
    """Write plain text to a PDF via LibreOffice headless.

    Creates a temporary .txt file and converts it.

    Args:
        text: Cover letter text.
        output_path: Destination PDF path.
    """
    txt_path = output_path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")

    try:
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_path.parent),
                str(txt_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError as exc:
        txt_path.unlink(missing_ok=True)
        raise OutputRenderError(
            "LibreOffice not found. Install LibreOffice to enable PDF output."
        ) from exc
    txt_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise OutputRenderError(f"LibreOffice PDF conversion failed: {result.stderr}")


async def render_cover_letter(
    cover_letter_text: str,
    output_dir: Path,
    job_id: str,
) -> str:
    """Write cover letter text to PDF.

    Args:
        cover_letter_text: Generated cover letter text.
        output_dir: Directory to write output files.
        job_id: Job identifier for file naming.

    Returns:
        Path to the generated PDF as string (empty if LibreOffice unavailable).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"cover_letter_{job_id}.pdf"

    try:
        _write_text_to_pdf(cover_letter_text, pdf_path)
        logger.info("cover_letter_renderer.pdf_written", path=str(pdf_path))
        return str(pdf_path)
    except OutputRenderError as exc:
        logger.warning("cover_letter_renderer.pdf_skipped", reason=str(exc))
        # Fallback: write as plain text
        txt_path = output_dir / f"cover_letter_{job_id}.txt"
        txt_path.write_text(cover_letter_text, encoding="utf-8")
        logger.info("cover_letter_renderer.txt_fallback", path=str(txt_path))
        return str(txt_path)
