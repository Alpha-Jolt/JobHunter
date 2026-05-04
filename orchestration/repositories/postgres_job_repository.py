"""PostgreSQL-backed JobRegistry implementation using SQLAlchemy async ORM."""

import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.exceptions import JobNotFoundError, RegistryError
from shared.models.job_record import JobRecord
from shared.registries.base import JobRegistryBase  # noqa: F401 — base from DPL package


def _orm_to_record(row) -> JobRecord:
    """Convert an ORM Job row to a JobRecord dataclass."""
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


class PostgresJobRepository(JobRegistryBase):
    """PostgreSQL-backed job repository using SQLAlchemy async ORM.

    Args:
        session: An active AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, jobs: List[JobRecord]) -> None:
        """Upsert a list of job records (INSERT … ON CONFLICT DO UPDATE).

        Args:
            jobs: List of JobRecord instances to persist.

        Raises:
            RegistryError: On unexpected database errors.
        """
        if not jobs:
            return
        try:
            import orchestration.db.models as _m
            Job = _m.Job

            for job in jobs:
                stmt = (
                    pg_insert(Job)
                    .values(
                        job_id=job.job_id,
                        source=job.source,
                        external_id=job.external_id,
                        title=job.title,
                        company_name=job.company_name,
                        company_domain=job.company_domain,
                        location=job.location,
                        remote_type=job.remote_type,
                        salary_min=job.salary_min,
                        salary_max=job.salary_max,
                        experience_min=job.experience_min,
                        experience_max=job.experience_max,
                        description=job.description,
                        skills_required=list(job.skills_required),
                        job_type=job.job_type,
                        apply_email=job.apply_email,
                        email_trust=job.email_trust,
                        apply_url=job.apply_url,
                        posted_at=job.posted_at,
                        scraped_at=job.scraped_at,
                        last_seen_at=job.last_seen_at or datetime.now(timezone.utc),
                        status=job.status,
                    )
                    .on_conflict_do_update(
                        constraint="jobs_source_external_id_unique",
                        set_={
                            "title": job.title,
                            "company_name": job.company_name,
                            "description": job.description,
                            "status": job.status,
                            "last_seen_at": job.last_seen_at or datetime.now(timezone.utc),
                            "apply_email": job.apply_email,
                            "email_trust": job.email_trust,
                        },
                    )
                )
                await self._session.execute(stmt)
        except Exception as exc:
            raise RegistryError(f"Failed to save jobs: {exc}", {"count": len(jobs)}) from exc

    async def get(self, job_id: uuid.UUID) -> JobRecord:
        """Retrieve a job by primary key.

        Args:
            job_id: UUID of the job.

        Returns:
            The matching JobRecord.

        Raises:
            JobNotFoundError: If no row with that job_id exists.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(select(Job).where(Job.job_id == str(job_id)))
        row = result.scalar_one_or_none()
        if row is None:
            raise JobNotFoundError(f"Job not found: {job_id}", {"job_id": str(job_id)})
        return _orm_to_record(row)

    async def get_many(self, job_ids: List[uuid.UUID]) -> List[JobRecord]:
        """Retrieve multiple jobs by primary keys.

        Args:
            job_ids: List of UUIDs.

        Returns:
            List of matching JobRecord instances (missing IDs are skipped).
        """
        if not job_ids:
            return []
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(
            select(Job).where(Job.job_id.in_([str(j) for j in job_ids]))
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def get_all_with_email(self) -> List[JobRecord]:
        """Return all jobs where apply_email IS NOT NULL.

        Returns:
            List of JobRecord instances.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(
            select(Job).where(Job.apply_email.isnot(None))
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def get_by_source(self, source: str) -> List[JobRecord]:
        """Return all jobs from a specific source platform.

        Args:
            source: One of "linkedin", "naukri", "indeed".

        Returns:
            List of matching JobRecord instances.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(select(Job).where(Job.source == source))
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def get_by_status(self, status: str) -> List[JobRecord]:
        """Return all jobs with a specific status.

        Args:
            status: One of "raw", "reviewed", "applied", "closed".

        Returns:
            List of matching JobRecord instances.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(select(Job).where(Job.status == status))
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def exists(self, job_id: uuid.UUID) -> bool:
        """Check whether a job exists.

        Args:
            job_id: UUID to check.

        Returns:
            True if the job exists.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(
            select(func.count()).select_from(Job).where(Job.job_id == str(job_id))
        )
        return (result.scalar() or 0) > 0

    async def count(self) -> int:
        """Return the total number of stored jobs.

        Returns:
            Integer count.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(select(func.count()).select_from(Job))
        return result.scalar() or 0

    async def delete_by_source(self, source: str) -> int:
        """Delete all jobs from a specific source.

        Args:
            source: One of "linkedin", "naukri", "indeed".

        Returns:
            Number of rows deleted.
        """
        import orchestration.db.models as _m
        Job = _m.Job

        result = await self._session.execute(delete(Job).where(Job.source == source))
        return result.rowcount or 0
