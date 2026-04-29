"""Data collector form submission routes."""

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from data_collector_ui.models import JobPreferences

router = APIRouter(prefix="/api")

_PREFS_FILE = Path("config/user_preferences.json")


@router.post("/submit_preferences")
async def submit_preferences(
    prefs: JobPreferences, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Save preferences and optionally trigger a scraper run."""
    _PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PREFS_FILE.write_text(prefs.model_dump_json(indent=2), encoding="utf-8")

    background_tasks.add_task(_trigger_scrape, prefs)
    return {"status": "accepted", "keywords": prefs.keywords, "locations": prefs.locations}


async def _trigger_scrape(prefs: JobPreferences) -> None:
    from dev_mode.dev_runner import DevModeRunner  # noqa: PLC0415

    runner = DevModeRunner()
    for source in prefs.sources:
        await runner.run_full_pipeline(source, prefs.keywords, prefs.locations)
