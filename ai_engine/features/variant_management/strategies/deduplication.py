"""Deduplication — prevents regenerating variants for the same job."""

from __future__ import annotations

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.variant_management.models.variant_record import VariantRecord

logger = get_logger(__name__)


def is_duplicate(job_id: str, existing_variants: list[VariantRecord]) -> bool:
    """Check if a variant already exists for the given job.

    Args:
        job_id: Job identifier to check.
        existing_variants: List of existing VariantRecord objects for this job.

    Returns:
        True if a variant already exists for this job.
    """
    if existing_variants:
        logger.warning(
            "deduplication.duplicate_detected",
            job_id=job_id,
            existing_count=len(existing_variants),
        )
        return True
    return False
