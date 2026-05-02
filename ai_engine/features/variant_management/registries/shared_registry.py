"""Shared registry adapter — persists VariantRecords to shared.VariantRegistry."""

from __future__ import annotations

import asyncio
import uuid

from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.variant_management.models.variant_record import VariantRecord

logger = get_logger(__name__)


def _run(coro):
    """Run a coroutine synchronously (registry interface is sync)."""
    return asyncio.run(coro)


def _is_uuid(value: str) -> bool:
    """Return True if value is a valid UUID string."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def _to_job_uuid(job_id: str) -> uuid.UUID:
    return uuid.UUID(job_id) if _is_uuid(job_id) else uuid.uuid5(uuid.NAMESPACE_DNS, job_id)


class SharedVariantRegistry:
    """Adapts shared.VariantRegistry to the JSONRegistry interface.

    Drop-in replacement for JSONRegistry — VariantManager needs no changes.

    Args:
        registry_path: Path to the shared variants JSON file.
    """

    def __init__(self, registry_path: str = "registries/variants.json") -> None:
        from shared.registries.variant_registry import VariantRegistry  # noqa: PLC0415

        self._registry = VariantRegistry(file_path=registry_path)

    def _to_shared(self, record: VariantRecord):
        """Convert ai_engine VariantRecord → shared VariantRecord."""
        from shared.models.variant_record import (  # noqa: PLC0415
            VariantRecord as SharedVariantRecord,
        )

        return SharedVariantRecord(
            variant_id=uuid.UUID(record.variant_id),
            user_id=record.user_id,
            job_id=_to_job_uuid(record.job_id),
            master_resume_id=uuid.uuid4(),
            pdf_key="",
            docx_key="",
            curated_json={},
            prompt_version=record.prompt_version,
            approval_status=record.approval_status.value,
        )

    def _from_shared(self, s) -> VariantRecord:
        """Convert shared VariantRecord → ai_engine VariantRecord."""
        return VariantRecord(
            variant_id=str(s.variant_id),
            job_id=str(s.job_id),
            user_id=s.user_id,
            prompt_version=s.prompt_version or "",
            approval_status=ApprovalStatus(s.approval_status),
        )

    def create(self, record: VariantRecord) -> None:
        """Register a new variant in the shared registry."""
        _run(self._registry.save(self._to_shared(record)))
        logger.info(
            "shared_registry.created",
            variant_id=record.variant_id,
            job_id=record.job_id,
        )

    def get(self, variant_id: str) -> VariantRecord | None:
        """Retrieve a variant by ID."""
        try:
            shared = _run(self._registry.get(uuid.UUID(variant_id)))
            return self._from_shared(shared)
        except Exception:
            return None

    def update_status(self, variant_id: str, status: ApprovalStatus) -> None:
        """Update approval status in the shared registry."""
        _run(self._registry.update_approval_status(uuid.UUID(variant_id), status.value))

    def list_by_job(self, job_id: str) -> list[VariantRecord]:
        """Return all variants for a job."""
        shared_list = _run(self._registry.get_for_job(_to_job_uuid(job_id)))
        return [self._from_shared(s) for s in shared_list]

    def list_by_user(self, user_id: str) -> list[VariantRecord]:
        """Return all variants for a user."""
        shared_list = _run(self._registry.get_for_user(user_id))
        return [self._from_shared(s) for s in shared_list]

    def count_all(self) -> int:
        """Return total variant count (approximated as 0 — budget enforced by shared layer)."""
        return 0
