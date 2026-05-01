"""JSON file-based variant registry for Phase 0."""

from __future__ import annotations

import json
from pathlib import Path

from ai_engine.core.exceptions import ValidationError
from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ApprovalStatus
from ai_engine.features.variant_management.models.variant_record import VariantRecord

logger = get_logger(__name__)


class JSONRegistry:
    """Local JSON file registry for variant records.

    Stores all variant metadata in a single JSON file.
    Thread-safety is not guaranteed — single-process use only in Phase 0.

    Args:
        registry_path: Path to the JSON registry file.
    """

    def __init__(self, registry_path: Path) -> None:
        self._path = registry_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, dict]:
        """Load registry from disk."""
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, dict]) -> None:
        """Persist registry to disk."""
        self._path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def create(self, record: VariantRecord) -> None:
        """Register a new variant record.

        Args:
            record: VariantRecord to store.

        Raises:
            ValidationError: If variant_id already exists.
        """
        data = self._load()
        if record.variant_id in data:
            raise ValidationError(f"Variant {record.variant_id} already exists in registry.")
        data[record.variant_id] = json.loads(record.model_dump_json())
        self._save(data)
        logger.info("json_registry.created", variant_id=record.variant_id, job_id=record.job_id)

    def get(self, variant_id: str) -> VariantRecord | None:
        """Retrieve a variant record by ID.

        Args:
            variant_id: Variant identifier.

        Returns:
            VariantRecord or None if not found.
        """
        data = self._load()
        raw = data.get(variant_id)
        return VariantRecord(**raw) if raw else None

    def update_status(self, variant_id: str, status: ApprovalStatus) -> None:
        """Update the approval status of a variant.

        Args:
            variant_id: Variant identifier.
            status: New approval status.

        Raises:
            ValidationError: If variant_id does not exist.
        """
        data = self._load()
        if variant_id not in data:
            raise ValidationError(f"Variant {variant_id} not found in registry.")
        data[variant_id]["approval_status"] = status.value
        self._save(data)
        logger.info("json_registry.status_updated", variant_id=variant_id, status=status.value)

    def list_by_job(self, job_id: str) -> list[VariantRecord]:
        """Return all variants for a given job ID.

        Args:
            job_id: Job identifier.

        Returns:
            List of VariantRecord instances.
        """
        data = self._load()
        return [VariantRecord(**v) for v in data.values() if v.get("job_id") == job_id]

    def list_by_user(self, user_id: str) -> list[VariantRecord]:
        """Return all variants for a given user ID.

        Args:
            user_id: User identifier.

        Returns:
            List of VariantRecord instances.
        """
        data = self._load()
        return [VariantRecord(**v) for v in data.values() if v.get("user_id") == user_id]

    def count_all(self) -> int:
        """Return total number of registered variants."""
        return len(self._load())
