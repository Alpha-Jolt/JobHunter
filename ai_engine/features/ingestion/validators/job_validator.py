"""Job record validator — validates required fields and data quality."""

from __future__ import annotations

from dataclasses import dataclass

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.ingestion.models.job_record import JobRecord

logger = get_logger(__name__)

_REQUIRED_FIELDS = ("job_id", "title", "company", "description")
_MIN_DESCRIPTION_LENGTH = 50


@dataclass
class ValidationResult:
    """Result of a single job record validation.

    Attributes:
        is_valid: Whether the record passed all checks.
        reason: Human-readable failure reason (empty if valid).
        job_id: The job_id of the validated record.
    """

    is_valid: bool
    reason: str
    job_id: str


def validate_job_record(record: JobRecord) -> ValidationResult:
    """Validate a single JobRecord for required fields and data quality.

    Args:
        record: The JobRecord to validate.

    Returns:
        ValidationResult with pass/fail status and reason.
    """
    for field in _REQUIRED_FIELDS:
        value = getattr(record, field, None)
        if not value:
            return ValidationResult(
                is_valid=False, reason=f"Missing required field: {field}", job_id=record.job_id
            )

    if len(record.description) < _MIN_DESCRIPTION_LENGTH:
        chars = len(record.description)
        return ValidationResult(
            is_valid=False,
            reason=f"Description too short ({chars} chars, min {_MIN_DESCRIPTION_LENGTH})",
            job_id=record.job_id,
        )

    return ValidationResult(is_valid=True, reason="", job_id=record.job_id)


def validate_records(records: list[JobRecord]) -> tuple[list[JobRecord], list[ValidationResult]]:
    """Validate a list of JobRecords, returning valid records and failure reports.

    Args:
        records: List of JobRecord instances to validate.

    Returns:
        Tuple of (valid_records, failed_results).
    """
    valid: list[JobRecord] = []
    failures: list[ValidationResult] = []

    for record in records:
        result = validate_job_record(record)
        if result.is_valid:
            valid.append(record)
        else:
            failures.append(result)
            logger.warning("job_validator.failed", job_id=record.job_id, reason=result.reason)

    logger.info("job_validator.summary", total=len(records), valid=len(valid), failed=len(failures))
    return valid, failures
