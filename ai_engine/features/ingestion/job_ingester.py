"""Job ingester orchestrator — reads, validates, and returns JobRecord objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.ingestion.models.job_record import JobRecord
from ai_engine.features.ingestion.readers.csv_reader import read_csv
from ai_engine.features.ingestion.readers.json_reader import read_json
from ai_engine.features.ingestion.validators.job_validator import ValidationResult, validate_records

logger = get_logger(__name__)


@dataclass
class IngestionSummary:
    """Summary of a job ingestion run.

    Attributes:
        total_files: Number of files processed.
        total_records_read: Total records read across all files.
        valid_records: Count of records that passed validation.
        skipped_records: Count of records that failed validation.
        failures: List of ValidationResult for failed records.
    """

    total_files: int = 0
    total_records_read: int = 0
    valid_records: int = 0
    skipped_records: int = 0
    failures: list[ValidationResult] = field(default_factory=list)


def _detect_format(path: Path) -> str:
    """Detect file format from extension.

    Args:
        path: File path.

    Returns:
        'csv' or 'json'.

    Raises:
        ValueError: If extension is not supported.
    """
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    raise ValueError(f"Unsupported file format: {suffix}")


async def ingest_jobs(file_paths: list[Path]) -> tuple[list[JobRecord], IngestionSummary]:
    """Read and validate job records from a list of CSV/JSON files.

    Args:
        file_paths: List of paths to scraper output files.

    Returns:
        Tuple of (valid_job_records, ingestion_summary).
    """
    summary = IngestionSummary(total_files=len(file_paths))
    all_records: list[JobRecord] = []

    for path in file_paths:
        if not path.exists():
            logger.warning("job_ingester.file_not_found", path=str(path))
            continue
        try:
            fmt = _detect_format(path)
            records = read_csv(path) if fmt == "csv" else read_json(path)
            all_records.extend(records)
            summary.total_records_read += len(records)
        except Exception as exc:
            logger.error("job_ingester.read_error", path=str(path), error=str(exc))

    valid, failures = validate_records(all_records)
    summary.valid_records = len(valid)
    summary.skipped_records = len(failures)
    summary.failures = failures

    logger.info(
        "job_ingester.complete",
        files=summary.total_files,
        read=summary.total_records_read,
        valid=summary.valid_records,
        skipped=summary.skipped_records,
    )
    return valid, summary
