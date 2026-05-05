"""Database registry stub — Phase 0+ PostgreSQL integration point."""

from __future__ import annotations

from ai_engine.core.types import ApprovalStatus
from ai_engine.features.variant_management.models.variant_record import VariantRecord


class DatabaseRegistry:
    """PostgreSQL-backed variant registry (Phase 0+ stub).

    Interface matches JSONRegistry. When PostgreSQL is integrated in Phase 0+,
    this class fills in the implementation without any changes to the manager.
    """

    def create(self, record: VariantRecord) -> None:
        """Register a new variant record."""
        raise NotImplementedError("DatabaseRegistry is a Phase 0+ feature.")

    def get(self, variant_id: str) -> VariantRecord | None:
        """Retrieve a variant record by ID."""
        raise NotImplementedError("DatabaseRegistry is a Phase 0+ feature.")

    def update_status(self, variant_id: str, status: ApprovalStatus) -> None:
        """Update the approval status of a variant."""
        raise NotImplementedError("DatabaseRegistry is a Phase 0+ feature.")

    def list_by_job(self, job_id: str) -> list[VariantRecord]:
        """Return all variants for a given job ID."""
        raise NotImplementedError("DatabaseRegistry is a Phase 0+ feature.")

    def list_by_user(self, user_id: str) -> list[VariantRecord]:
        """Return all variants for a given user ID."""
        raise NotImplementedError("DatabaseRegistry is a Phase 0+ feature.")

    def count_all(self) -> int:
        """Return total number of registered variants."""
        raise NotImplementedError("DatabaseRegistry is a Phase 0+ feature.")
