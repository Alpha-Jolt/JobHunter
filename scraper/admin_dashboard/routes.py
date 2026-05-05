"""Admin dashboard API routes."""

import glob
import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, HTTPException

from scraper.logging_.metrics import Metrics

router = APIRouter(prefix="/api")

_OUTPUT_DIR = Path("output/final")
_LOG_FILE = Path("logs/scraper.log")


@router.get("/scraper/status")
async def get_scraper_status() -> Dict[str, Any]:
    return {"status": "idle", "metrics": Metrics.snapshot()}


@router.get("/jobs/stats")
async def get_jobs_stats() -> Dict[str, Any]:
    files = list(_OUTPUT_DIR.glob("jobs_*.json")) if _OUTPUT_DIR.exists() else []
    total = 0
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            total += len(data)
        except Exception:
            pass
    return {"total_jobs": total, "output_files": len(files)}


@router.post("/scraper/trigger")
async def trigger_scraper(source: str, background_tasks: BackgroundTasks) -> Dict[str, str]:
    if source not in ("indeed", "naukri"):
        raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
    background_tasks.add_task(_run_scraper, source)
    return {"status": "triggered", "source": source}


@router.get("/logs")
async def get_logs(limit: int = 100) -> List[str]:
    if not _LOG_FILE.exists():
        return []
    lines = _LOG_FILE.read_text(encoding="utf-8").splitlines()
    return lines[-limit:]


async def _run_scraper(source: str) -> None:
    from dev_mode.dev_runner import DevModeRunner  # noqa: PLC0415

    runner = DevModeRunner()
    await runner.run_full_pipeline(source)
