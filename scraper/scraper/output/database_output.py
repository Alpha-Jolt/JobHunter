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
                index_elements=["source", "external_id"],
                set_={
                    "title": stmt.excluded.title,
                    "company_name": stmt.excluded.company_name,
                    "description": stmt.excluded.description,
                    "last_seen_at": stmt.excluded.last_seen_at,
                    "apply_email": stmt.excluded.apply_email,
                }
            )
            await session.execute(stmt)
            await self._upsert_companies_from_jobs(session, jobs)
            await session.commit()
            
        logger.info("DatabaseOutput saved %d jobs", len(records))
        return len(records)

    async def _upsert_companies_from_jobs(self, session, jobs: List[CanonicalJob]) -> None:
        """Upserts stub companies for new jobs that have a company domain."""
        from sqlalchemy import text
        import hashlib
        import uuid
        
        for job in jobs:
            if not job.company_domain:
                continue
                
            domain = job.company_domain.lower().replace("www.", "").rstrip("/")
            dedup = hashlib.sha256(domain.encode("utf-8")).hexdigest()
            normalized_name = job.company_name.lower().strip() if job.company_name else None
            
            # Using 'name_only' if we just have a name but here we have a domain so 'pending'
            stmt = text("""
                INSERT INTO companies (
                    company_id, company_name, normalized_name, apex_domain,
                    subdomains, career_emails, contact_emails, email_trust,
                    ats_platform, source, source_detail, robots_txt_allowed,
                    crawl_status, dedup_fingerprint, discovery_date, is_generated
                ) VALUES (
                    :company_id, :company_name, :normalized_name, :apex_domain,
                    '{}', '{}', '{}', 'unverified',
                    'none', 'search_discovery', :source_detail, NULL,
                    'pending', :dedup, now(), false
                )
                ON CONFLICT (apex_domain) DO NOTHING
            """)
            await session.execute(stmt, {
                "company_id": str(uuid.uuid4()),
                "company_name": job.company_name,
                "normalized_name": normalized_name,
                "apex_domain": domain,
                "source_detail": f"{job.source}_feed",
                "dedup": dedup,
            })

    async def read(self) -> List[CanonicalJob]:
        """Not implemented — scraper does not read from DB."""
        raise NotImplementedError("DatabaseOutput does not support read")
