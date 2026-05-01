"""CSV reader for scraper output files."""

from __future__ import annotations

import csv
import uuid
from pathlib import Path

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.ingestion.models.job_record import JobRecord
from ai_engine.shared.date_utils import parse_datetime

logger = get_logger(__name__)

# Maps CSV column names → JobRecord field names
_COLUMN_MAP: dict[str, str] = {
    "job_id": "job_id",
    "id": "job_id",
    "source": "source",
    "title": "title",
    "job_title": "title",
    "company": "company",
    "company_name": "company",
    "location": "location",
    "remote_type": "remote_type",
    "remote": "remote_type",
    "experience_level": "experience_level",
    "experience": "experience_level",
    "description": "description",
    "job_description": "description",
    "skills_required": "skills_required",
    "skills": "skills_required",
    "apply_email": "apply_email",
    "email": "apply_email",
    "apply_url": "apply_url",
    "url": "apply_url",
    "job_url": "apply_url",
    "posted_at": "posted_at",
    "posted_date": "posted_at",
    "scraped_at": "scraped_at",
}


def _map_row(row: dict[str, str], row_num: int) -> dict:
    """Map a CSV row dict to JobRecord field dict.

    Args:
        row: Raw CSV row.
        row_num: Row number for logging.

    Returns:
        Dict suitable for JobRecord construction.
    """
    mapped: dict = {}
    for csv_col, value in row.items():
        field = _COLUMN_MAP.get(csv_col.lower().strip())
        if field and value:
            mapped[field] = value.strip()

    # Ensure job_id exists
    if "job_id" not in mapped or not mapped["job_id"]:
        mapped["job_id"] = str(uuid.uuid4())
        logger.warning("csv_reader.generated_job_id", row_num=row_num)

    # Parse skills array from comma-separated string
    if "skills_required" in mapped and isinstance(mapped["skills_required"], str):
        mapped["skills_required"] = [
            s.strip() for s in mapped["skills_required"].split(",") if s.strip()
        ]

    # Parse datetime fields
    for dt_field in ("posted_at", "scraped_at"):
        if dt_field in mapped and isinstance(mapped[dt_field], str):
            mapped[dt_field] = parse_datetime(mapped[dt_field])

    return mapped


def read_csv(file_path: Path) -> list[JobRecord]:
    """Read a scraper CSV file and return validated JobRecord objects.

    Rows with missing required fields (title, company, description) are skipped.

    Args:
        file_path: Path to the CSV file.

    Returns:
        List of valid JobRecord instances.
    """
    records: list[JobRecord] = []
    skipped = 0

    with file_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row_num, row in enumerate(reader, start=2):
            mapped = _map_row(row, row_num)
            required = ("title", "company", "description")
            if any(not mapped.get(f) for f in required):
                logger.warning(
                    "csv_reader.skipped_row", row_num=row_num, reason="missing_required_fields"
                )
                skipped += 1
                continue
            try:
                records.append(JobRecord(**mapped))
            except Exception as exc:
                logger.warning("csv_reader.skipped_row", row_num=row_num, reason=str(exc))
                skipped += 1

    logger.info("csv_reader.complete", file=str(file_path), loaded=len(records), skipped=skipped)
    return records
