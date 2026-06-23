"""Database output adapter — persists CanonicalJob list to PostgreSQL."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Set

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from scraper.db.models import Job
from scraper.normalization.canonical_schema import CanonicalJob
from scraper.output.base_output import BaseOutput

logger = logging.getLogger(__name__)


class DatabaseOutput(BaseOutput):
    """Saves CanonicalJobs to the PostgreSQL jobs table."""

    def __init__(self, session_factory: async_sessionmaker, run_id: uuid.UUID) -> None:
        self._session_factory = session_factory
        self.run_id = run_id

    async def get_existing_external_ids(self, source: str, external_ids: List[str]) -> Set[str]:
        """Query the database to find which external_ids already exist for this source."""
        if not external_ids:
            return set()
        
        async with self._session_factory() as session:
            result = await session.execute(
                select(Job.external_id)
                .where(Job.source == source)
                .where(Job.external_id.in_(external_ids))
            )
            return set(result.scalars().all())

    async def write(self, jobs: List[CanonicalJob]) -> int:
        """Convert and persist jobs; handles deduplication with ON CONFLICT DO UPDATE.
        
        Returns:
            The number of records processed.
        """
        if not jobs:
            return 0
            
        records = []
        for job in jobs:
            records.append({
                "job_id": uuid.uuid4() if job.job_id is None else uuid.UUID(job.job_id),
                "source": job.source,
                "external_id": job.external_id,
                "title": job.title,
                "company_name": job.company_name,
                "company_domain": job.company_domain,
                "location": ", ".join(filter(None, [job.location_city, job.location_state])) or None,
                "remote_type": job.remote_type if job.remote_type != "unknown" else None,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "experience_min": job.experience_min,
                "experience_max": job.experience_max,
                "description": job.description,
                "skills_required": list(job.skills_required),
                "job_type": job.job_type if job.job_type != "unknown" else "fulltime",
                "apply_email": job.apply_email,
                "email_trust": "unknown",
                "apply_url": job.apply_url,
                "posted_at": job.posted_at,
                "scraped_at": job.scraped_at,
                "last_seen_at": datetime.now(timezone.utc),
                "status": "raw",
            })
            
        async with self._session_factory() as session:
            stmt = pg_insert(Job).values(records)
            stmt = stmt.on_conflict_do_update(
                constraint="jobs_source_external_id_unique",
                set_={
                    "title": stmt.excluded.title,
                    "company_name": stmt.excluded.company_name,
                    "description": stmt.excluded.description,
                    "last_seen_at": stmt.excluded.last_seen_at,
                    "apply_email": stmt.excluded.apply_email,
                }
            )
            await session.execute(stmt)
            await session.commit()
            
        logger.info("DatabaseOutput saved %d jobs", len(records))
        return len(records)

    async def read(self) -> List[CanonicalJob]:
        """Not implemented — scraper does not read from DB."""
        raise NotImplementedError("DatabaseOutput does not support read")
