"""Unit tests for job ingester."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from ai_engine.features.ingestion.job_ingester import ingest_jobs


@pytest.mark.asyncio
async def test_ingest_jobs_from_csv(tmp_path: Path):
    """Ingester reads valid CSV and returns JobRecord objects."""
    csv_file = tmp_path / "jobs.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["job_id", "source", "title", "company", "description", "apply_url"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "job_id": "j1",
                "source": "indeed",
                "title": "Python Dev",
                "company": "Acme",
                "description": (
                    "We need a Python developer with 3+ years experience "
                    "building REST APIs and microservices."
                ),
                "apply_url": "https://acme.com/jobs/1",
            }
        )

    records, summary = await ingest_jobs([csv_file])
    assert len(records) == 1
    assert records[0].job_id == "j1"
    assert summary.valid_records == 1


@pytest.mark.asyncio
async def test_ingest_jobs_from_json(tmp_path: Path):
    """Ingester reads valid JSON and returns JobRecord objects."""
    json_file = tmp_path / "jobs.json"
    json_file.write_text(
        json.dumps(
            [
                {
                    "job_id": "j2",
                    "source": "naukri",
                    "title": "Backend Engineer",
                    "company": "Beta Corp",
                    "description": (
                        "Backend engineer needed with Python, PostgreSQL, and Docker "
                        "experience for our platform team."
                    ),
                    "skills_required": ["Python", "PostgreSQL"],
                    "apply_url": "https://beta.com/jobs/2",
                }
            ]
        ),
        encoding="utf-8",
    )

    records, summary = await ingest_jobs([json_file])
    assert len(records) == 1
    assert records[0].skills_required == ["Python", "PostgreSQL"]


@pytest.mark.asyncio
async def test_ingest_jobs_skips_missing_required_fields(tmp_path: Path):
    """Ingester skips records missing required fields."""
    csv_file = tmp_path / "bad.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["job_id", "title", "company", "description"])
        writer.writeheader()
        writer.writerow({"job_id": "j3", "title": "", "company": "X", "description": "short"})

    records, summary = await ingest_jobs([csv_file])
    assert len(records) == 0
    assert summary.valid_records == 0
