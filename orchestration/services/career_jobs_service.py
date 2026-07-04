"""Career jobs service — read-only job inventory queries.

Trigger and status methods have moved to admin_api/company_discovery/service.py.
"""

import uuid
from typing import Dict, List, Optional, Tuple

import orchestration.db.models as _db_models
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CareerJobsService:
    """Read-only career page job queries backed by PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest_jobs(
        self,
        company_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:
        """Return paginated active career page job listings.

        Args:
            company_id: Filter by company.
            status: Filter by job status ('active', 'closed', 'raw').
            limit: Page size.
            offset: Pagination offset.

        Returns:
            Tuple of (list of job dicts, total count).
        """
        CareerJob = _db_models.CareerJob
        Company = _db_models.Company

        base_stmt = select(CareerJob, Company.company_name, Company.apex_domain).join(
            Company, CareerJob.company_id == Company.company_id
        )

        if company_id:
            base_stmt = base_stmt.where(CareerJob.company_id == company_id)
        if status:
            base_stmt = base_stmt.where(CareerJob.status == status)
        else:
            base_stmt = base_stmt.where(CareerJob.status != "closed")

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            base_stmt.order_by(CareerJob.last_seen_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)

        jobs = []
        for row in result.all():
            job, company_name, apex_domain = row
            jobs.append(_career_job_to_dict(job, company_name, apex_domain))

        return jobs, total

    async def get_counts(self) -> Dict:
        """Return aggregated career job counts by status, company, and extraction method.

        Returns:
            Counts dict.
        """
        CareerJob = _db_models.CareerJob

        total = (await self._session.execute(
            select(func.count()).select_from(CareerJob)
        )).scalar() or 0

        by_status = {
            r.status: r.cnt
            for r in (await self._session.execute(
                select(CareerJob.status, func.count().label("cnt"))
                .group_by(CareerJob.status)
            ))
        }

        by_extraction_method = {
            r.extraction_method: r.cnt
            for r in (await self._session.execute(
                select(CareerJob.extraction_method, func.count().label("cnt"))
                .group_by(CareerJob.extraction_method)
            ))
        }

        active_company_count = (await self._session.execute(
            select(func.count(func.distinct(CareerJob.company_id))).where(
                CareerJob.status == "active"
            )
        )).scalar() or 0

        with_apply_contact = (await self._session.execute(
            select(func.count()).select_from(CareerJob).where(
                (CareerJob.apply_email.isnot(None)) | (CareerJob.apply_url.isnot(None))
            )
        )).scalar() or 0

        return {
            "total_jobs": total,
            "by_status": by_status,
            "by_extraction_method": by_extraction_method,
            "active_companies_count": active_company_count,
            "jobs_with_apply_contact": with_apply_contact,
        }


def _career_job_to_dict(
    row: _db_models.CareerJob,
    company_name: Optional[str] = None,
    apex_domain: Optional[str] = None,
) -> Dict:
    """Convert a CareerJob ORM row to a serialisable dict."""
    return {
        "career_job_id": str(row.career_job_id),
        "company_id": str(row.company_id),
        "company_name": company_name,
        "apex_domain": apex_domain,
        "job_title": row.job_title,
        "job_url": row.job_url,
        "location": row.location,
        "remote_type": row.remote_type,
        "job_type": row.job_type,
        "salary_min": row.salary_min,
        "salary_max": row.salary_max,
        "experience_min": row.experience_min,
        "experience_max": row.experience_max,
        "skills_required": list(row.skills_required or []),
        "apply_email": row.apply_email,
        "apply_url": row.apply_url,
        "ats_platform": row.ats_platform,
        "extraction_method": row.extraction_method,
        "posted_at": row.posted_at.isoformat() if row.posted_at else None,
        "scraped_at": row.scraped_at.isoformat() if row.scraped_at else None,
        "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
        "status": row.status,
        "source_channel": row.source_channel,
    }
