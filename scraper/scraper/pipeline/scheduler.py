"""APScheduler-based periodic scraping scheduler."""

from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from scraper.logging_.logger import Logger
from scraper.pipeline.pipeline import ScraperPipeline


class ScraperScheduler:
    """Schedule scraper pipeline runs at configurable intervals."""

    def __init__(self, pipeline: ScraperPipeline) -> None:
        self.pipeline = pipeline
        self.scheduler = AsyncIOScheduler()
        self.logger = Logger.get_logger(__name__)

    def schedule_scraper(
        self,
        scraper_name: str,
        keywords: List[str],
        locations: List[str],
        interval_hours: int = 6,
    ) -> None:
        """Add a periodic job to the scheduler."""
        from scraper.pipeline.worker import run_scraper_job  # noqa: PLC0415

        self.scheduler.add_job(
            run_scraper_job,
            "interval",
            hours=interval_hours,
            args=[self.pipeline, scraper_name, keywords, locations],
            id=f"{scraper_name}_scraper",
            replace_existing=True,
        )
        self.logger.info(
            "Scraper scheduled",
            extra_data={
                "source": scraper_name,
                "interval_hours": interval_hours,
            },
        )

    def start(self) -> None:
        self.scheduler.start()
        self.logger.info("Scheduler started")

    def stop(self) -> None:
        self.scheduler.shutdown(wait=False)
        self.logger.info("Scheduler stopped")

    def schedule_bootstrap_refresh(self) -> None:
        """Schedule monthly bootstrap source import (1st of each month at 02:00 UTC)."""
        self.scheduler.add_job(
            _run_bootstrap_import,
            CronTrigger(day=1, hour=2, minute=0),
            id="company_discovery_bootstrap_monthly",
            replace_existing=True,
        )
        self.logger.info("Monthly bootstrap refresh scheduled")

    def schedule_email_refresh(self) -> None:
        """Schedule monthly email re-crawl (15th of each month at 03:00 UTC).

        Processes companies where email_last_crawled_at is older than 30 days.
        """
        self.scheduler.add_job(
            _run_email_refresh,
            CronTrigger(day=15, hour=3, minute=0),
            id="company_email_refresh_monthly",
            replace_existing=True,
        )
        self.logger.info("Monthly email refresh scheduled")

    def schedule_career_page_refresh(self) -> None:
        """Schedule weekly career page job scrape (every Monday at 04:00 UTC)."""
        self.scheduler.add_job(
            _run_career_page_scrape,
            CronTrigger(day_of_week="mon", hour=4, minute=0),
            id="career_page_weekly_scrape",
            replace_existing=True,
        )
        self.logger.info("Weekly career page scrape scheduled")

    def schedule_ats_api_refresh(self) -> None:
        """Schedule weekly ATS API re-pull (every Monday at 02:00 UTC, before full scrape)."""
        self.scheduler.add_job(
            _run_ats_api_refresh,
            CronTrigger(day_of_week="mon", hour=2, minute=0),
            id="ats_api_weekly_refresh",
            replace_existing=True,
        )
        self.logger.info("Weekly ATS API refresh scheduled")


# --- Scheduled task handlers ------------------------------------------------

async def _run_bootstrap_import() -> None:
    """Trigger company discovery bootstrap via Redis queue."""
    import json
    import redis.asyncio as redis
    from scraper.config import config

    r = redis.from_url(config.redis_url or "redis://redis:6379/0", decode_responses=True)
    task = {
        "task_id": _new_task_id(),
        "payload": {"type": "company_discovery_bootstrap", "sources": ["all"]},
    }
    await r.rpush("scraper:tasks", json.dumps(task))
    await r.aclose()


async def _run_email_refresh() -> None:
    """Trigger company email re-crawl via Redis queue."""
    import json
    import redis.asyncio as redis
    from scraper.config import config

    r = redis.from_url(config.redis_url or "redis://redis:6379/0", decode_responses=True)
    task = {
        "task_id": _new_task_id(),
        "payload": {"type": "company_email_refresh"},
    }
    await r.rpush("scraper:tasks", json.dumps(task))
    await r.aclose()


async def _run_career_page_scrape() -> None:
    """Trigger weekly career page job scrape via Redis queue."""
    import json
    import redis.asyncio as redis
    from scraper.config import config

    r = redis.from_url(config.redis_url or "redis://redis:6379/0", decode_responses=True)
    task = {
        "task_id": _new_task_id(),
        "payload": {"type": "career_page_scrape", "company_id": None},
    }
    await r.rpush("scraper:tasks", json.dumps(task))
    await r.aclose()


async def _run_ats_api_refresh() -> None:
    """Trigger weekly ATS API re-pull for Greenhouse/Lever/Ashby companies."""
    import json
    import redis.asyncio as redis
    from scraper.config import config

    r = redis.from_url(config.redis_url or "redis://redis:6379/0", decode_responses=True)
    task = {
        "task_id": _new_task_id(),
        "payload": {"type": "ats_api_refresh"},
    }
    await r.rpush("scraper:tasks", json.dumps(task))
    await r.aclose()


def _new_task_id() -> str:
    import uuid
    return str(uuid.uuid4())
