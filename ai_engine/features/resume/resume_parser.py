"""Resume parser orchestrator."""

from __future__ import annotations

from pathlib import Path

from ai_engine.core.exceptions import FabricationDetectedError, ResumeParsingError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ResumeFormat
from ai_engine.features.resume.extractors.docx_extractor import extract_docx
from ai_engine.features.resume.extractors.pdf_extractor import extract_pdf
from ai_engine.features.resume.extractors.text_cleaner import clean_text
from ai_engine.features.resume.models.resume_schema import ResumeData
from ai_engine.features.resume.strategies.llm_parser_strategy import LLMParserStrategy
from ai_engine.features.resume.validators.fabrication_detector import detect_fabrication
from ai_engine.features.resume.validators.schema_validator import validate_resume_schema

logger = get_logger(__name__)


def _detect_format(path: Path) -> ResumeFormat:
    """Detect resume format from file extension.

    Args:
        path: Resume file path.

    Returns:
        ResumeFormat enum value.

    Raises:
        ResumeParsingError: If format is not supported.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return ResumeFormat.PDF
    if suffix in (".docx", ".doc"):
        return ResumeFormat.DOCX
    raise ResumeParsingError(f"Unsupported resume format: {suffix}")


class ResumeParser:
    """Orchestrates the full resume parsing pipeline.

    Pipeline: detect format → extract text → clean → LLM parse
    → validate schema → detect fabrication.

    Args:
        strategy: LLMParserStrategy instance.
        allow_fabrication: If True, fabrication warnings are logged but not raised.
            Should be False in production.
    """

    def __init__(self, strategy: LLMParserStrategy, allow_fabrication: bool = False) -> None:
        self._strategy = strategy
        self._allow_fabrication = allow_fabrication

    async def parse(self, file_path: Path) -> ResumeData:
        """Parse a resume file into structured ResumeData.

        Args:
            file_path: Path to the PDF or DOCX resume file.

        Returns:
            Validated ResumeData instance.

        Raises:
            ResumeParsingError: If extraction or parsing fails.
            FabricationDetectedError: If fabricated content is found (and allow_fabrication=False).
            SchemaValidationError: If parsed data fails schema validation.
        """
        if not file_path.exists():
            raise ResumeParsingError(f"Resume file not found: {file_path}")

        fmt = _detect_format(file_path)
        logger.info("resume_parser.start", file=str(file_path), format=fmt.value)

        raw_text = extract_pdf(file_path) if fmt == ResumeFormat.PDF else extract_docx(file_path)
        cleaned = clean_text(raw_text)

        resume, prompt_version = await self._strategy.parse(cleaned)
        validate_resume_schema(resume)

        report = detect_fabrication(resume, cleaned)
        if not report.is_clean:
            logger.warning(
                "resume_parser.fabrication_detected",
                fields=report.fabricated_fields,
                details=report.details,
            )
            if not self._allow_fabrication:
                raise FabricationDetectedError(report.fabricated_fields)

        logger.info(
            "resume_parser.complete",
            file=str(file_path),
            skills=len(resume.skills),
            experience_entries=len(resume.experience_entries),
            prompt_version=prompt_version,
        )
        return resume
