"""PostgreSQL-backed ApplicationLog implementation using SQLAlchemy async ORM."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.application_record import ApplicationRecord
from shared.models.exceptions import ApplicationNotFoundError, RegistryError
from shared.registries.base import ApplicationLogBase


def _orm_to_record(row) -> ApplicationRecord:
    """Convert an ORM ApplicationLog row to an ApplicationRecord dataclass."""
    return ApplicationRecord(
        application_id=uuid.UUID(str(row.application_id)),
        user_id=row.user_id,
        job_id=uuid.UUID(str(row.job_id)),
        resume_variant_id=uuid.UUID(str(row.resume_variant_id)),
        cover_letter_id=uuid.UUID(str(row.cover_letter_id)) if row.cover_letter_id else None,
        status=row.status,
        sent_at=row.sent_at,
        last_activity_at=row.last_activity_at,
        thread_id=row.thread_id,
        email_subject=row.email_subject,
        reply_count=row.reply_count,
        notes=row.notes,
    )


class PostgresApplicationRepository(ApplicationLogBase):
    """PostgreSQL-backed application log using SQLAlchemy async ORM.

    Args:
        session: An active AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_send(self, record: ApplicationRecord) -> None:
        """Insert a new application record.

        Enforces one application per (user_id, job_id).

        Args:
            record: ApplicationRecord to persist.

        Raises:
            RegistryError: If a duplicate application exists.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        if await self.has_user_applied_to_job(record.user_id, record.job_id):
            raise RegistryError(
                "Application already exists for this (user_id, job_id)",
                {"user_id": record.user_id, "job_id": str(record.job_id)},
            )

        row = ApplicationLog(
            application_id=str(record.application_id),
            user_id=record.user_id,
            job_id=str(record.job_id),
            resume_variant_id=str(record.resume_variant_id),
            cover_letter_id=str(record.cover_letter_id) if record.cover_letter_id else None,
            status=record.status,
            sent_at=record.sent_at,
            last_activity_at=record.last_activity_at,
            thread_id=record.thread_id,
            email_subject=record.email_subject,
            reply_count=record.reply_count,
            notes=record.notes,
        )
        self._session.add(row)

    async def get(self, application_id: uuid.UUID) -> ApplicationRecord:
        """Retrieve an application by primary key.

        Args:
            application_id: UUID of the application.

        Returns:
            The matching ApplicationRecord.

        Raises:
            ApplicationNotFoundError: If no row with that application_id exists.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            select(ApplicationLog).where(ApplicationLog.application_id == str(application_id))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise ApplicationNotFoundError(
                f"Application not found: {application_id}",
                {"application_id": str(application_id)},
            )
        return _orm_to_record(row)

    async def get_by_user(self, user_id: str) -> List[ApplicationRecord]:
        """Return all applications for a given user_id.

        Args:
            user_id: Identifier of the user.

        Returns:
            List of ApplicationRecord instances.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            select(ApplicationLog).where(ApplicationLog.user_id == user_id)
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def get_by_job(self, job_id: uuid.UUID) -> List[ApplicationRecord]:
        """Return all applications for a given job_id.

        Args:
            job_id: UUID of the job.

        Returns:
            List of ApplicationRecord instances.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            select(ApplicationLog).where(ApplicationLog.job_id == str(job_id))
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def has_user_applied_to_job(self, user_id: str, job_id: uuid.UUID) -> bool:
        """Check whether a user has already applied to a job.

        Args:
            user_id: Identifier of the user.
            job_id: UUID of the job.

        Returns:
            True if an application already exists.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            select(func.count())
            .select_from(ApplicationLog)
            .where(ApplicationLog.user_id == user_id, ApplicationLog.job_id == str(job_id))
        )
        return (result.scalar() or 0) > 0

    async def get_applications_sent_today(self, user_id: str) -> List[ApplicationRecord]:
        """Return applications sent by a user in the last 24 hours.

        Args:
            user_id: Identifier of the user.

        Returns:
            List of ApplicationRecord instances.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await self._session.execute(
            select(ApplicationLog).where(
                ApplicationLog.user_id == user_id,
                ApplicationLog.sent_at >= cutoff,
            )
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def update_status(self, application_id: uuid.UUID, new_status: str) -> None:
        """Update the status of an application.

        Args:
            application_id: UUID of the application.
            new_status: New status string.

        Raises:
            ApplicationNotFoundError: If no row with that application_id exists.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            update(ApplicationLog)
            .where(ApplicationLog.application_id == str(application_id))
            .values(status=new_status)
        )
        if result.rowcount == 0:
            raise ApplicationNotFoundError(
                f"Application not found: {application_id}",
                {"application_id": str(application_id)},
            )

    async def update_reply_count(self, application_id: uuid.UUID, count: int) -> None:
        """Set the reply count for an application.

        Args:
            application_id: UUID of the application.
            count: New reply count value.

        Raises:
            ApplicationNotFoundError: If no row with that application_id exists.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            update(ApplicationLog)
            .where(ApplicationLog.application_id == str(application_id))
            .values(reply_count=count)
        )
        if result.rowcount == 0:
            raise ApplicationNotFoundError(
                f"Application not found: {application_id}",
                {"application_id": str(application_id)},
            )

    async def update_email_delivery(
        self,
        mailbridge_email_id: str,
        delivery_status: str,
        delivered_at: datetime | None,
    ) -> None:
        """Update email delivery status by Mail-Bridge email_id.

        Called by the webhook receiver when Mail-Bridge pushes a delivery event.

        Args:
            mailbridge_email_id: The email_id returned by Mail-Bridge on send.
            delivery_status: 'delivered' or 'failed'.
            delivered_at: Timestamp from Mail-Bridge sent_at field, or None on failure.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        values: dict = {"email_delivery_status": delivery_status}
        if delivered_at is not None:
            values["email_delivered_at"] = delivered_at

        await self._session.execute(
            update(ApplicationLog)
            .where(ApplicationLog.mailbridge_email_id == mailbridge_email_id)
            .values(**values)
        )

    async def count_by_user(self, user_id: str) -> int:
        """Count applications for a user.

        Args:
            user_id: Identifier of the user.

        Returns:
            Integer count.
        """
        import orchestration.db.models as _m
        ApplicationLog = _m.ApplicationLog

        result = await self._session.execute(
            select(func.count())
            .select_from(ApplicationLog)
            .where(ApplicationLog.user_id == user_id)
        )
        return result.scalar() or 0
