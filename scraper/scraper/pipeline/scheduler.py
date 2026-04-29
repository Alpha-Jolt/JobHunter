"""APScheduler-based periodic scraping scheduler."""

from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
            extra_data={"source": scraper_name, "interval_hours": interval_hours},
        )

    def start(self) -> None:
        self.scheduler.start()
        self.logger.info("Scheduler started")

    def stop(self) -> None:
        self.scheduler.shutdown(wait=False)
        self.logger.info("Scheduler stopped")
