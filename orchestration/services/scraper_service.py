"""Scraper service — coordinates scraper runs and job inventory queries."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import orchestration.db.models as _db_models
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.job_record import JobRecord


def _orm_job_to_record(row) -> JobRecord:
    return JobRecord(
        job_id=uuid.UUID(str(row.job_id)),
        source=row.source,
        external_id=row.external_id,
        title=row.title,
        company_name=row.company_name,
        company_domain=row.company_domain,
        location=row.location,
        remote_type=row.remote_type,
        salary_min=float(row.salary_min) if row.salary_min is not None else None,
        salary_max=float(row.salary_max) if row.salary_max is not None else None,
        experience_min=row.experience_min,
        experience_max=row.experience_max,
        description=row.description,
        skills_required=list(row.skills_required or []),
        job_type=row.job_type,
        apply_email=row.apply_email,
        email_trust=row.email_trust,
        apply_url=row.apply_url,
        posted_at=row.posted_at,
        scraped_at=row.scraped_at,
        last_seen_at=row.last_seen_at,
        status=row.status,
    )


class ScraperService:
    """High-level scraper operations backed by PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def trigger_scrape(
        self, source: str, keywords: List[str], locations: List[str], pages: int,
    ) -> uuid.UUID:
        """Create a scraper_run record and return its run_id (stub in Phase 0)."""
        ScraperRun = _db_models.ScraperRun
        run = ScraperRun(
            run_id=str(uuid.uuid4()),
            source=source,
            keywords=keywords,
            locations=locations,
            pages_requested=pages,
            status="queued",
            started_at=datetime.now(timezone.utc),
        )
        self._session.add(run)
        await self._session.flush()
        return uuid.UUID(run.run_id)

    async def get_scrape_status(self, run_id: uuid.UUID) -> Optional[Dict]:
        """Return status and counts for a scraper run."""
        ScraperRun = _db_models.ScraperRun
        result = await self._session.execute(
            select(ScraperRun).where(ScraperRun.run_id == str(run_id))
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {
            "run_id": str(row.run_id),
            "source": row.source,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "status": row.status,
            "jobs_fetched": row.jobs_fetched,
            "jobs_inserted": row.jobs_inserted,
            "errors": row.errors,
        }

    async def get_latest_jobs(
        self, source: Optional[str] = None, limit: int = 20, offset: int = 0, search: Optional[str] = None,
    ) -> tuple[List[JobRecord], int]:
        """Return active jobs ordered by last_seen_at DESC, and total count."""
        Job = _db_models.Job
        
        # Base query for filtering
        base_stmt = select(Job).where(Job.status != "closed")
        if source:
            base_stmt = base_stmt.where(Job.source == source)
        if search:
            from sqlalchemy import or_
            search_term = f"%{search}%"
            base_stmt = base_stmt.where(
                or_(
                    Job.title.ilike(search_term),
                    Job.company_name.ilike(search_term),
                    Job.description.ilike(search_term)
                )
            )
            
        # Get total count
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar() or 0
        
        # Get paginated results
        stmt = base_stmt.order_by(Job.last_seen_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [_orm_job_to_record(row) for row in result.scalars().all()], total

    async def get_job_counts(self) -> Dict:
        """Return aggregated job counts by source, status, and email_trust."""
        Job = _db_models.Job
        total = (await self._session.execute(
            select(func.count()).select_from(Job)
        )).scalar() or 0

        by_source = {
            r.source: r.cnt for r in (await self._session.execute(
                select(Job.source, func.count().label("cnt")).group_by(Job.source)
            ))
        }
        by_status = {
            r.status: r.cnt for r in (await self._session.execute(
                select(Job.status, func.count().label("cnt")).group_by(Job.status)
            ))
        }
        by_email_trust = {
            r.email_trust: r.cnt for r in (await self._session.execute(
                select(Job.email_trust, func.count().label("cnt")).group_by(Job.email_trust)
            ))
        }
        return {
            "total_jobs": total,
            "by_source": by_source,
            "by_status": by_status,
            "by_email_trust": by_email_trust,
        }
