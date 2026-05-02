"""Registry reader — reads JobRecords from shared.JobRegistry."""

from __future__ import annotations

import asyncio

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.ingestion.models.job_record import JobRecord

logger = get_logger(__name__)


def read_registry(registry_path: str = "registries/jobs.json") -> list[JobRecord]:
    """Read raw JobRecords from the shared JobRegistry JSON file.

    Args:
        registry_path: Path to the shared registry JSON file.

    Returns:
        List of JobRecord instances with status 'raw'.
    """
    from shared.registries.job_registry import JobRegistry  # noqa: PLC0415

    async def _fetch() -> list:
        reg = JobRegistry(file_path=registry_path)
        return await reg.get_by_status("raw")

    shared_records = asyncio.run(_fetch())

    records: list[JobRecord] = []
    for r in shared_records:
        try:
            records.append(JobRecord(
                job_id=str(r.job_id),
                source=r.source,
                title=r.title,
                company=r.company_name,
                location=r.location or "",
                remote_type=r.remote_type or "",
                description=r.description,
                skills_required=list(r.skills_required),
                apply_email=r.apply_email or "",
                apply_url=r.apply_url or "",
                posted_at=r.posted_at,
                scraped_at=r.scraped_at,
            ))
        except Exception as exc:
            logger.warning("registry_reader.skipped", job_id=str(r.job_id), error=str(exc))

    logger.info("registry_reader.complete", loaded=len(records))
    return records
