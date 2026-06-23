"""Write CanonicalJob list to a timestamped CSV file."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from scraper.normalization.canonical_schema import CanonicalJob
from scraper.output.base_output import BaseOutput

_FIELDS = [
    "job_id",
    "source",
    "external_id",
    "source_url",
    "title",
    "company_name",
    "company_domain", "location_city", "location_state", "location_country",
    "remote_type", "salary_min", "salary_max", "salary_currency",
    "experience_min", "experience_max", "job_type",
    "apply_url", "apply_email", "apply_method",
    "posted_at", "posted_days_ago", "scraped_at",
    "completeness_score", "confidence_score",
    "skills_required", "benefits",
]


class CSVOutput(BaseOutput):
    """Writes jobs to a timestamped CSV file in output_dir/final/."""

    def __init__(self, output_dir: Path = Path("output")) -> None:
        self.output_dir = Path(output_dir) / "final"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._last_file: Path = Path()

    async def write(self, jobs: List[CanonicalJob]) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._last_file = self.output_dir / f"jobs_{ts}.csv"
        with open(
            self._last_file, "w", newline="", encoding="utf-8"
        ) as fh:
            writer = csv.DictWriter(
                fh, fieldnames=_FIELDS, extrasaction="ignore"
            )
            writer.writeheader()
            for job in jobs:
                row = job.model_dump(mode="json")
                row["skills_required"] = "|".join(
                    row.get("skills_required") or []
                )
                row["benefits"] = "|".join(row.get("benefits") or [])
                writer.writerow(row)

    async def read(self) -> List[CanonicalJob]:
        if not self._last_file.exists():
            return []
        jobs = []
        with open(self._last_file, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                row["skills_required"] = [
                    s for s in row.get("skills_required", "").split("|") if s
                ]
                row["benefits"] = [
                    b for b in row.get("benefits", "").split("|") if b
                ]
                jobs.append(CanonicalJob(**row))
        return jobs
