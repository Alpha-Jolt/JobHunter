"""PostgreSQL-backed VariantRegistry implementation using SQLAlchemy async ORM."""

import uuid
from typing import List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.exceptions import RegistryError, VariantNotFoundError
from shared.models.variant_record import VariantRecord
from shared.registries.base import VariantRegistryBase

_MAX_VARIANTS_PER_USER = 50


def _orm_to_record(row) -> VariantRecord:
    """Convert an ORM ResumeVariant row to a VariantRecord dataclass."""
    return VariantRecord(
        variant_id=uuid.UUID(str(row.variant_id)),
        user_id=row.user_id,
        job_id=uuid.UUID(str(row.job_id)),
        master_resume_id=uuid.UUID(str(row.master_resume_id)),
        pdf_key=row.pdf_key or "",
        docx_key=row.docx_key or "",
        cover_letter_key=row.cover_letter_key or "",
        local_pdf_path=row.local_pdf_path or "",
        s3_upload_failed=row.s3_upload_failed,
        curated_json=dict(row.curated_json or {}),
        gaps_identified=list(row.gaps_identified or []),
        approval_status=row.approval_status,
        approval_token=row.approval_token,
        approved_at=row.approved_at,
        user_feedback=row.user_feedback,
        created_at=row.created_at,
        prompt_version=row.prompt_version or "",
    )


class PostgresVariantRepository(VariantRegistryBase):
    """PostgreSQL-backed variant repository using SQLAlchemy async ORM.

    Args:
        session: An active AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, variant: VariantRecord) -> None:
        """Insert a new variant record.

        Enforces:
        - One variant per (user_id, job_id).
        - Max 50 variants per user.

        Args:
            variant: VariantRecord to persist.

        Raises:
            RegistryError: On duplicate (user_id, job_id) or variant cap exceeded.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        # Enforce uniqueness
        existing = await self._session.execute(
            select(func.count())
            .select_from(ResumeVariant)
            .where(
                ResumeVariant.user_id == variant.user_id,
                ResumeVariant.job_id == str(variant.job_id),
            )
        )
        if (existing.scalar() or 0) > 0:
            raise RegistryError(
                "Variant already exists for this (user_id, job_id)",
                {"user_id": variant.user_id, "job_id": str(variant.job_id)},
            )

        # Enforce cap
        total = await self.count_by_user(variant.user_id)
        if total >= _MAX_VARIANTS_PER_USER:
            raise RegistryError(
                f"Variant cap reached ({_MAX_VARIANTS_PER_USER}) for user",
                {"user_id": variant.user_id},
            )

        row = ResumeVariant(
            variant_id=str(variant.variant_id),
            user_id=variant.user_id,
            job_id=str(variant.job_id),
            master_resume_id=str(variant.master_resume_id),
            pdf_key=variant.pdf_key,
            docx_key=variant.docx_key,
            cover_letter_key=variant.cover_letter_key,
            local_pdf_path=variant.local_pdf_path,
            s3_upload_failed=variant.s3_upload_failed,
            curated_json=variant.curated_json,
            gaps_identified=list(variant.gaps_identified),
            approval_status=variant.approval_status,
            approval_token=variant.approval_token,
            approved_at=variant.approved_at,
            user_feedback=variant.user_feedback,
            prompt_version=variant.prompt_version,
        )
        self._session.add(row)

    async def get(self, variant_id: uuid.UUID) -> VariantRecord:
        """Retrieve a variant by primary key.

        Args:
            variant_id: UUID of the variant.

        Returns:
            The matching VariantRecord.

        Raises:
            VariantNotFoundError: If no row with that variant_id exists.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(ResumeVariant).where(ResumeVariant.variant_id == str(variant_id))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise VariantNotFoundError(
                f"Variant not found: {variant_id}", {"variant_id": str(variant_id)}
            )
        return _orm_to_record(row)

    async def get_for_job(self, job_id: uuid.UUID) -> List[VariantRecord]:
        """Return all variants for a given job_id.

        Args:
            job_id: UUID of the job.

        Returns:
            List of VariantRecord instances.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(ResumeVariant).where(ResumeVariant.job_id == str(job_id))
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def get_approved_for_job(
        self, job_id: uuid.UUID, user_id: str
    ) -> Optional[VariantRecord]:
        """Return the approved variant for a user+job pair.

        Args:
            job_id: UUID of the job.
            user_id: Identifier of the user.

        Returns:
            The approved VariantRecord, or None.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(ResumeVariant).where(
                ResumeVariant.job_id == str(job_id),
                ResumeVariant.user_id == user_id,
                ResumeVariant.approval_status == "approved",
            )
        )
        row = result.scalar_one_or_none()
        return _orm_to_record(row) if row else None

    async def get_for_user(self, user_id: str) -> List[VariantRecord]:
        """Return all variants for a given user_id.

        Args:
            user_id: Identifier of the user.

        Returns:
            List of VariantRecord instances.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(ResumeVariant).where(ResumeVariant.user_id == user_id)
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def get_pending_for_user(self, user_id: str) -> List[VariantRecord]:
        """Return pending variants for a user.

        Args:
            user_id: Identifier of the user.

        Returns:
            List of pending VariantRecord instances.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(ResumeVariant).where(
                ResumeVariant.user_id == user_id,
                ResumeVariant.approval_status == "pending",
            )
        )
        return [_orm_to_record(row) for row in result.scalars().all()]

    async def update_approval_status(self, variant_id: uuid.UUID, status: str) -> None:
        """Update the approval_status of a variant.

        Args:
            variant_id: UUID of the variant.
            status: New approval status.

        Raises:
            VariantNotFoundError: If no row with that variant_id exists.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            update(ResumeVariant)
            .where(ResumeVariant.variant_id == str(variant_id))
            .values(approval_status=status)
        )
        if result.rowcount == 0:
            raise VariantNotFoundError(
                f"Variant not found: {variant_id}", {"variant_id": str(variant_id)}
            )

    async def update_approval_token(self, variant_id: uuid.UUID, token: str) -> None:
        """Store the approval token for a variant.

        Args:
            variant_id: UUID of the variant.
            token: 64-character hex approval token.

        Raises:
            VariantNotFoundError: If no row with that variant_id exists.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            update(ResumeVariant)
            .where(ResumeVariant.variant_id == str(variant_id))
            .values(approval_token=token)
        )
        if result.rowcount == 0:
            raise VariantNotFoundError(
                f"Variant not found: {variant_id}", {"variant_id": str(variant_id)}
            )

    async def exists(self, variant_id: uuid.UUID) -> bool:
        """Check whether a variant exists.

        Args:
            variant_id: UUID to check.

        Returns:
            True if the variant exists.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(func.count())
            .select_from(ResumeVariant)
            .where(ResumeVariant.variant_id == str(variant_id))
        )
        return (result.scalar() or 0) > 0

    async def count_by_user(self, user_id: str) -> int:
        """Count variants for a user.

        Args:
            user_id: Identifier of the user.

        Returns:
            Integer count.
        """
        import orchestration.db.models as _m
        ResumeVariant = _m.ResumeVariant

        result = await self._session.execute(
            select(func.count())
            .select_from(ResumeVariant)
            .where(ResumeVariant.user_id == user_id)
        )
        return result.scalar() or 0
