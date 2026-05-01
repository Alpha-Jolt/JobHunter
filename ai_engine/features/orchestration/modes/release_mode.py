"""Release mode — renders output files for approved variants."""

from __future__ import annotations

from ai_engine.core.exceptions import ApprovalRequiredError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.analysis.models.job_analysis import JobAnalysis
from ai_engine.features.ingestion.models.job_record import JobRecord
from ai_engine.features.optimization.models.optimised_variant import OptimisedVariant
from ai_engine.features.orchestration.models.pipeline_result import PipelineResult
from ai_engine.features.output.output_builder import OutputBuilder

logger = get_logger(__name__)


async def run_release_mode(
    variant_jobs: list[tuple[str, OptimisedVariant, JobAnalysis, JobRecord]],
    output_builder: OutputBuilder,
) -> PipelineResult:
    """Execute release mode: check approval → render output files.

    Args:
        variant_jobs: List of (variant_id, variant, job_analysis, job_record) tuples.
        output_builder: OutputBuilder instance.

    Returns:
        PipelineResult with output file paths.
    """
    errors: list[str] = []
    output_paths: list[str] = []

    for variant_id, variant, job_analysis, job in variant_jobs:
        try:
            package = await output_builder.build(
                variant_id=variant_id,
                variant=variant,
                job_analysis=job_analysis,
                job=job,
            )
            output_paths.extend(
                p
                for p in [
                    package.resume_docx_path,
                    package.resume_pdf_path,
                    package.cover_letter_pdf_path,
                    package.email_draft_path,
                ]
                if p
            )
            logger.info("release_mode.variant_released", variant_id=variant_id, job_id=job.job_id)

        except ApprovalRequiredError:
            errors.append(f"Variant {variant_id}: not approved — skipped.")
            logger.warning("release_mode.not_approved", variant_id=variant_id)
        except Exception as exc:
            errors.append(f"Variant {variant_id}: {exc}")
            logger.error("release_mode.failed", variant_id=variant_id, error=str(exc))

    released = len(variant_jobs) - len(errors)
    status = "success" if not errors else ("partial_failure" if released > 0 else "failure")

    return PipelineResult(
        status=status,
        output_packages=released,
        errors=errors,
        output_paths=output_paths,
        execution_summary=f"Released {released} output packages. {len(errors)} failed.",
    )
