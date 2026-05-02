"""JSON reader for scraper output files."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.ingestion.models.job_record import JobRecord
from ai_engine.shared.date_utils import parse_datetime

logger = get_logger(__name__)


def _normalise_entry(entry: dict, idx: int) -> dict:
    """Normalise a raw JSON entry to JobRecord fields.

    Args:
        entry: Raw dict from JSON file.
        idx: Entry index for logging.

    Returns:
        Normalised dict for JobRecord construction.
    """
    # Ensure job_id
    job_id = entry.get("job_id") or entry.get("id") or str(uuid.uuid4())

    # Skills may be a list or comma-separated string
    skills_raw = entry.get("skills_required") or entry.get("skills") or []
    if isinstance(skills_raw, str):
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
    else:
        skills = [str(s).strip() for s in skills_raw if s]

    return {
        "job_id": str(job_id),
        "source": entry.get("source", ""),
        "title": entry.get("title") or entry.get("job_title", ""),
        "company": entry.get("company") or entry.get("company_name", ""),
        "location": entry.get("location", ""),
        "remote_type": entry.get("remote_type") or entry.get("remote", ""),
        "experience_level": entry.get("experience_level") or entry.get("experience", ""),
        "description": entry.get("description") or entry.get("job_description", ""),
        "skills_required": skills,
        "apply_email": entry.get("apply_email") or entry.get("email", ""),
        "apply_url": entry.get("apply_url") or entry.get("url") or entry.get("job_url", ""),
        "posted_at": parse_datetime(entry.get("posted_at") or entry.get("posted_date")),
        "scraped_at": parse_datetime(entry.get("scraped_at")),
    }


def read_json(file_path: Path) -> list[JobRecord]:
    """Read a scraper JSON file and return validated JobRecord objects.

    Supports both a JSON array and a JSON object with a 'jobs' key.

    Args:
        file_path: Path to the JSON file.

    Returns:
        List of valid JobRecord instances.
    """
    raw = json.loads(file_path.read_text(encoding="utf-8"))

    if isinstance(raw, dict):
        entries = raw.get("jobs") or raw.get("data") or list(raw.values())
    elif isinstance(raw, list):
        entries = raw
    else:
        logger.warning("json_reader.unexpected_format", file=str(file_path))
        return []

    records: list[JobRecord] = []
    skipped = 0

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            skipped += 1
            continue
        normalised = _normalise_entry(entry, idx)
        if not normalised["title"] or not normalised["company"] or not normalised["description"]:
            logger.warning("json_reader.skipped_entry", idx=idx, reason="missing_required_fields")
            skipped += 1
            continue
        try:
            records.append(JobRecord(**normalised))
        except Exception as exc:
            logger.warning("json_reader.skipped_entry", idx=idx, reason=str(exc))
            skipped += 1

    logger.info("json_reader.complete", file=str(file_path), loaded=len(records), skipped=skipped)
    return records
