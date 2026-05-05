"""Generate mode — reads scraper output, parses resume, generates variants."""

from __future__ import annotations

from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.analysis.job_analyser import JobAnalyser
from ai_engine.features.ingestion.job_ingester import ingest_jobs
from ai_engine.features.matching.comparator import Comparator
from ai_engine.features.optimization.resume_optimiser import ResumeOptimiser
from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
from ai_engine.features.orchestration.models.pipeline_result import PipelineResult
from ai_engine.features.resume.resume_parser import ResumeParser
from ai_engine.features.variant_management.manager import VariantManager

logger = get_logger(__name__)


async def run_generate_mode(
    config: PipelineConfig,
    resume_parser: ResumeParser,
    job_analyser: JobAnalyser,
    comparator: Comparator,
    optimiser: ResumeOptimiser,
    variant_manager: VariantManager,
) -> PipelineResult:
    """Execute generate mode: ingest jobs → parse resume → analyse → compare → optimise → register.

    Variants are left in PENDING state at the end of this mode.

    Args:
        config: Pipeline configuration.
        resume_parser: ResumeParser instance.
        job_analyser: JobAnalyser instance.
        comparator: Comparator instance.
        optimiser: ResumeOptimiser instance.
        variant_manager: VariantManager instance.

    Returns:
        PipelineResult with generated variant IDs and summary.
    """
    errors: list[str] = []
    variant_ids: list[str] = []

    # Ingest jobs
    if getattr(config, "use_shared_registry", False):
        from ai_engine.features.ingestion.readers.registry_reader import (  # noqa: PLC0415
            read_registry,
        )

        registry_path = getattr(config, "shared_jobs_registry_path", "registries/jobs.json")
        jobs = read_registry(registry_path)
        summary = None
    else:
        scraper_files = list(config.scraper_output_dir.glob("*.csv")) + list(
            config.scraper_output_dir.glob("*.json")
        )
        jobs, summary = await ingest_jobs(scraper_files)

    if config.job_ids_to_process:
        jobs = [j for j in jobs if j.job_id in config.job_ids_to_process]

    if not jobs:
        return PipelineResult(
            status="failure",
            errors=["No valid job records found in scraper output."],
            execution_summary="No jobs to process.",
        )

    # Parse resume once
    try:
        resume = await resume_parser.parse(config.resume_file_path)
    except Exception as exc:
        return PipelineResult(
            status="failure",
            errors=[f"Resume parsing failed: {exc}"],
            execution_summary="Pipeline aborted — resume could not be parsed.",
        )

    # Process each job
    for job in jobs:
        try:
            analysis = await job_analyser.analyse(job)
            comparison = await comparator.compare(resume, analysis)
            variant = await optimiser.optimise(resume, analysis, comparison)
            result = await variant_manager.register(
                variant=variant,
                comparison=comparison,
                user_id=config.user_id,
            )

            if config.auto_approve:
                variant_manager.update_approval(result.variant_id, ApprovalStatus.APPROVED)

            variant_ids.append(result.variant_id)
            logger.info(
                "generate_mode.variant_registered",
                job_id=job.job_id,
                variant_id=result.variant_id,
                match_score=comparison.match_score,
            )

        except Exception as exc:
            errors.append(f"Job {job.job_id}: {exc}")
            logger.error("generate_mode.job_failed", job_id=job.job_id, error=str(exc))

    status = "success" if not errors else ("partial_failure" if variant_ids else "failure")
    return PipelineResult(
        status=status,
        generated_variants=len(variant_ids),
        errors=errors,
        variant_ids=variant_ids,
        execution_summary=(
            f"Generated {len(variant_ids)} variants. "
            f"{len(errors)} jobs failed. "
            f"Budget remaining: "
            f"{(summary.valid_records if summary else len(jobs)) - len(variant_ids)} slots."
        ),
    )
