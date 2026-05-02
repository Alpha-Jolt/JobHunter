"""Output builder orchestrator."""

from __future__ import annotations

from pathlib import Path

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.approval.approval_gate import ApprovalGate
from ai_engine.features.ingestion.models.job_record import JobRecord
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.output.models.output_package import OutputPackage
from ai_engine.features.output.renderers.cover_letter_renderer import render_cover_letter
from ai_engine.features.output.renderers.email_renderer import render_email
from ai_engine.features.output.renderers.resume_renderer import render_resume
from ai_engine.features.output.strategies.llm_cover_letter_strategy import LLMCoverLetterStrategy
from ai_engine.features.output.templating.variable_mapper import map_email_variables

logger = get_logger(__name__)


class OutputBuilder:
    """Orchestrates all output file generation for an approved variant.

    Args:
        approval_gate: ApprovalGate to verify variant is approved.
        cover_letter_strategy: LLMCoverLetterStrategy for cover letter generation.
        ai_output_dir: Root directory for all output files.
        email_template_path: Path to the user's email template (optional).
    """

    def __init__(
        self,
        approval_gate: ApprovalGate,
        cover_letter_strategy: LLMCoverLetterStrategy,
        ai_output_dir: Path,
        email_template_path: Path | None = None,
    ) -> None:
        self._gate = approval_gate
        self._cover_letter = cover_letter_strategy
        self._output_dir = ai_output_dir
        self._email_template = email_template_path

    async def build(
        self,
        variant_id: str,
        variant: OptimisedVariant,
        job_analysis: JobAnalysis,
        job: JobRecord,
    ) -> OutputPackage:
        """Build all output files for an approved variant.

        Args:
            variant_id: Registered variant ID.
            variant: OptimisedVariant with resume content.
            job_analysis: Analysed job description.
            job: Original JobRecord for metadata.

        Returns:
            OutputPackage with paths to all generated files.

        Raises:
            ApprovalRequiredError: If variant is not approved.
            OutputRenderError: If file generation fails.
        """
        self._gate.require_approved(variant_id)

        session_dir = self._output_dir / variant_id / job.job_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Resume
        docx_path, pdf_path = await render_resume(variant, session_dir)

        # Cover letter
        cover_letter_text = await self._cover_letter.generate(variant, job_analysis)
        cl_path = await render_cover_letter(cover_letter_text, session_dir, job.job_id)

        # Email draft
        email_path = ""
        if self._email_template and self._email_template.exists():
            variables = map_email_variables(job_analysis, variant, job.title, job.company)
            email_path = await render_email(
                self._email_template, variables, session_dir, job.job_id
            )

        package = OutputPackage(
            variant_id=variant_id,
            job_id=job.job_id,
            resume_docx_path=docx_path,
            resume_pdf_path=pdf_path,
            cover_letter_pdf_path=cl_path,
            email_draft_path=email_path,
            manifest={
                "job_title": job.title,
                "company": job.company,
                "match_score": 0,
            },
        )

        logger.info(
            "output_builder.complete",
            variant_id=variant_id,
            job_id=job.job_id,
            docx=bool(docx_path),
            cover_letter=bool(cl_path),
            email=bool(email_path),
        )
        return package
