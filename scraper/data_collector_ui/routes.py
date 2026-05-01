"""Data collector form submission routes."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks

from data_collector_ui.models import JobPreferences

router = APIRouter(prefix="/api")

_PREFS_FILE = Path("config/user_preferences.json")
_logger = logging.getLogger(__name__)


@router.post("/submit_preferences")
async def submit_preferences(
    prefs: JobPreferences, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Save preferences and trigger all scrapers in parallel."""
    _PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PREFS_FILE.write_text(
        prefs.model_dump_json(indent=2), encoding="utf-8"
    )
    background_tasks.add_task(_trigger_scrape, prefs)
    return {
        "status": "accepted",
        "keywords": prefs.keywords,
        "locations": prefs.locations,
        "sources": prefs.sources,
    }


async def _run_source(source: str, prefs: JobPreferences) -> None:
    """Run one source pipeline, flushing partial data on cancellation."""
    from dev_mode.dev_runner import DevModeRunner  # noqa: PLC0415

    _logger.info(
        "[%s] scrape started — keywords=%s locations=%s",
        source,
        prefs.keywords,
        prefs.locations,
    )
    try:
        runner = DevModeRunner()
        result = await runner.run_full_pipeline(
            source,
            prefs.keywords,
            prefs.locations,
            experience=prefs.experience,
        )
        _logger.info(
            "[%s] scrape complete — raw=%d final=%d duration=%.1fs",
            source,
            result.raw_jobs_count,
            result.final_jobs_count,
            result.duration_seconds,
        )
    except asyncio.CancelledError:
        _logger.warning("[%s] scrape cancelled — partial data flushed", source)
        raise
    except Exception as exc:
        _logger.error("[%s] scrape failed — %s", source, exc, exc_info=True)


async def _trigger_scrape(prefs: JobPreferences) -> None:
    """Run all requested sources in parallel."""
    sources = [s for s in prefs.sources if s in ("naukri", "indeed")]
    if not sources:
        _logger.warning("No valid sources in preferences — skipping")
        return

    _logger.info("Starting parallel scrape for sources: %s", sources)
    await asyncio.gather(
        *[_run_source(source, prefs) for source in sources],
        return_exceptions=True,
    )
    _logger.info("All sources finished")
