"""Write CanonicalJob list to timestamped JSON files."""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from scraper.normalization.canonical_schema import CanonicalJob
from scraper.output.base_output import BaseOutput


class JSONOutput(BaseOutput):
    """Writes jobs to a timestamped JSON file in output_dir/final/."""

    def __init__(self, output_dir: Path = Path("output")) -> None:
        self.output_dir = Path(output_dir) / "final"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._last_file: Path = Path()

    async def write(self, jobs: List[CanonicalJob]) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._last_file = self.output_dir / f"jobs_{ts}.json"
        data = [job.model_dump(mode="json") for job in jobs]
        with open(self._last_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)

    async def read(self) -> List[CanonicalJob]:
        if not self._last_file.exists():
            return []
        with open(self._last_file, encoding="utf-8") as fh:
            raw = json.load(fh)
        return [CanonicalJob(**item) for item in raw]
