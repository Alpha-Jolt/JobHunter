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
        include_career_jobs: bool = False
    ) -> tuple[List[JobRecord], int]:
        """Return active jobs ordered by last_seen_at DESC, and total count."""
        Job = _db_models.Job
        CareerJob = _db_models.CareerJob
        Company = _db_models.Company
        
        from sqlalchemy import union_all, literal_column, cast, String, Numeric
        
        j_stmt = select(
            Job.job_id.label("job_id"),
            Job.source.label("source"),
            Job.external_id.label("external_id"),
            Job.title.label("title"),
            Job.company_name.label("company_name"),
            Job.company_domain.label("company_domain"),
            Job.location.label("location"),
            Job.remote_type.label("remote_type"),
            Job.salary_min.label("salary_min"),
            Job.salary_max.label("salary_max"),
            Job.experience_min.label("experience_min"),
            Job.experience_max.label("experience_max"),
            Job.description.label("description"),
            Job.skills_required.label("skills_required"),
            Job.job_type.label("job_type"),
            Job.apply_email.label("apply_email"),
            Job.email_trust.label("email_trust"),
            Job.apply_url.label("apply_url"),
            Job.posted_at.label("posted_at"),
            Job.scraped_at.label("scraped_at"),
            Job.last_seen_at.label("last_seen_at"),
            Job.status.label("status")
        ).where(Job.status != "closed")

        if source and source != "career_page":
            j_stmt = j_stmt.where(Job.source == source)
        elif source == "career_page":
            j_stmt = j_stmt.where(literal_column("1") == literal_column("0"))
            
        if search:
            from sqlalchemy import or_
            search_term = f"%{search}%"
            j_stmt = j_stmt.where(
                or_(
                    Job.title.ilike(search_term),
                    Job.company_name.ilike(search_term),
                    Job.description.ilike(search_term)
                )
            )

        stmts = [j_stmt]

        if include_career_jobs:
            cj_stmt = select(
                CareerJob.career_job_id.label("job_id"),
                CareerJob.source_channel.label("source"),
                cast(literal_column("''"), String(255)).label("external_id"),
                CareerJob.job_title.label("title"),
                Company.company_name.label("company_name"),
                Company.apex_domain.label("company_domain"),
                CareerJob.location.label("location"),
                CareerJob.remote_type.label("remote_type"),
                cast(CareerJob.salary_min, Numeric(12, 2)).label("salary_min"),
                cast(CareerJob.salary_max, Numeric(12, 2)).label("salary_max"),
                CareerJob.experience_min.label("experience_min"),
                CareerJob.experience_max.label("experience_max"),
                CareerJob.description.label("description"),
                CareerJob.skills_required.label("skills_required"),
                CareerJob.job_type.label("job_type"),
                CareerJob.apply_email.label("apply_email"),
                cast(literal_column("'unknown'"), String(20)).label("email_trust"),
                CareerJob.apply_url.label("apply_url"),
                CareerJob.posted_at.label("posted_at"),
                CareerJob.scraped_at.label("scraped_at"),
                CareerJob.last_seen_at.label("last_seen_at"),
                CareerJob.status.label("status")
            ).select_from(
                CareerJob.__table__.join(Company.__table__, CareerJob.company_id == Company.company_id)
            ).where(CareerJob.status != "closed")

            if source and source != "career_page":
                cj_stmt = cj_stmt.where(literal_column("1") == literal_column("0"))
                
            if search:
                from sqlalchemy import or_
                search_term = f"%{search}%"
                cj_stmt = cj_stmt.where(
                    or_(
                        CareerJob.job_title.ilike(search_term),
                        Company.company_name.ilike(search_term),
                        CareerJob.description.ilike(search_term)
                    )
                )
                
            stmts.append(cj_stmt)

        union_stmt = union_all(*stmts)
        subq = union_stmt.subquery()
        
        count_stmt = select(func.count()).select_from(subq)
        total = (await self._session.execute(count_stmt)).scalar() or 0
        
        stmt = select(subq).order_by(subq.c.last_seen_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        
        return [_orm_job_to_record(row) for row in result.all()], total

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
