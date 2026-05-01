"""DOCX text extractor with structural awareness."""

from __future__ import annotations

from pathlib import Path

from ai_engine.core.exceptions import ResumeParsingError
from ai_engine.core.logging_.logger import get_logger

logger = get_logger(__name__)


def extract_docx(file_path: Path) -> str:
    """Extract text from a DOCX file, preserving structural markers.

    Headings are prefixed with ``[HEADING]``, paragraphs with ``[PARA]``,
    and list items with ``[BULLET]``.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Extracted text with section markers.

    Raises:
        ResumeParsingError: If extraction fails.
    """
    try:
        from docx import Document  # noqa: PLC0415
    except ImportError as exc:
        raise ResumeParsingError("python-docx not installed. Run: pip install python-docx") from exc

    try:
        doc = Document(str(file_path))
    except Exception as exc:
        raise ResumeParsingError(f"Failed to open DOCX: {exc}") from exc

    lines: list[str] = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style_name = para.style.name.lower() if para.style else ""
        if "heading" in style_name:
            lines.append(f"[HEADING] {text}")
        elif para.style and para.style.name in ("List Bullet", "List Number", "List Paragraph"):
            lines.append(f"[BULLET] {text}")
        else:
            lines.append(f"[PARA] {text}")

    extracted = "\n".join(lines)
    logger.info("docx_extractor.complete", file=str(file_path), chars=len(extracted))
    return extracted
