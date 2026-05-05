"""PDF text extractor — pdfplumber primary, pymupdf fallback."""

from __future__ import annotations

from pathlib import Path

from ai_engine.core.exceptions import ResumeParsingError
from ai_engine.core.logging_.logger import get_logger

logger = get_logger(__name__)


def _extract_with_pdfplumber(file_path: Path) -> str:
    """Extract text using pdfplumber."""
    import pdfplumber  # noqa: PLC0415

    lines: list[str] = []
    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.append(text)
    return "\n".join(lines)


def _extract_with_pymupdf(file_path: Path) -> str:
    """Extract text using pymupdf (fitz) as fallback."""
    import fitz  # noqa: PLC0415

    doc = fitz.open(str(file_path))
    lines: list[str] = []
    for page in doc:
        lines.append(page.get_text())
    doc.close()
    return "\n".join(lines)


def extract_pdf(file_path: Path) -> str:
    """Extract text from a PDF file.

    Tries pdfplumber first; falls back to pymupdf for difficult layouts.
    Full OCR support is deferred to Phase 1.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text string.

    Raises:
        ResumeParsingError: If both extractors fail.
    """
    try:
        text = _extract_with_pdfplumber(file_path)
        if text.strip():
            logger.info("pdf_extractor.pdfplumber_success", file=str(file_path), chars=len(text))
            return text
        logger.warning("pdf_extractor.pdfplumber_empty", file=str(file_path))
    except ImportError:
        logger.warning("pdf_extractor.pdfplumber_unavailable")
    except Exception as exc:
        logger.warning("pdf_extractor.pdfplumber_failed", error=str(exc))

    try:
        text = _extract_with_pymupdf(file_path)
        logger.info("pdf_extractor.pymupdf_success", file=str(file_path), chars=len(text))
        return text
    except ImportError as exc:
        raise ResumeParsingError(
            "Neither pdfplumber nor pymupdf is installed. " "Run: pip install pdfplumber pymupdf"
        ) from exc
    except Exception as exc:
        raise ResumeParsingError(f"PDF extraction failed: {exc}") from exc
