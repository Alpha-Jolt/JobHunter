"""CLI / worker entrypoint for running the scraper pipeline."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import List, Optional

from scraper.config import config
from scraper.core.browser_manager import BrowserManager
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.db.connection import get_session_factory, init_db
from scraper.logging_.logger import Logger
from scraper.pipeline.pipeline import PipelineResult, ScraperPipeline

_logger = Logger.get_logger(__name__)


class DevModeRunner:
    """Runs Naukri / Indeed scrape pipelines for local CLI and Redis worker tasks."""

    def __init__(self) -> None:
        self.config = config
        self.session_factory = None
        if self.config.use_database and self.config.database_url:
            init_db(self.config.database_url)
            self.session_factory = get_session_factory()

    def _build_pipeline(self) -> ScraperPipeline:
        return ScraperPipeline(self.config, session_factory=self.session_factory)

    def _rate_limiter(self) -> RateLimiter:
        rate_limiter = RateLimiter()
        rate_limiter.set_rate("in.indeed.com", self.config.indeed_rate_limit)
        rate_limiter.set_rate("www.naukri.com", self.config.naukri_rate_limit)
        return rate_limiter

    def _retry_handler(self) -> RetryHandler:
        return RetryHandler(
            max_retries=self.config.max_retries,
            base_delay=self.config.retry_base_delay,
            max_delay=self.config.retry_max_delay,
        )

    async def run_naukri_scraper(
        self,
        keywords: List[str],
        locations: List[str],
        experience: str = "",
        **_kwargs,
    ) -> PipelineResult:
        """Run the Naukri scraper through the full pipeline."""
        from scraper.sources.naukri_scraper import NaukriScraper

        pipeline = self._build_pipeline()
        rate_limiter = self._rate_limiter()
        retry_handler = self._retry_handler()

        async with BrowserManager(
            headless=self.config.headless,
            pool_size=self.config.browser_pool_size,
            timeout_ms=self.config.scraper_timeout_ms,
        ) as bm:
            scraper = NaukriScraper(
                bm, rate_limiter, retry_handler, debug=self.config.dev_mode
            )
            await scraper.initialize()
            return await pipeline.execute(
                scraper,
                keywords,
                locations,
                pages=self.config.pages_per_search,
                experience=experience,
            )

    async def run_indeed_scraper(
        self,
        keywords: List[str],
        locations: List[str],
        experience: str = "",
        **_kwargs,
    ) -> PipelineResult:
        """Run the Indeed scraper through the full pipeline."""
        from scraper.sources.indeed_scraper import IndeedScraper

        pipeline = self._build_pipeline()
        rate_limiter = self._rate_limiter()
        retry_handler = self._retry_handler()

        async with BrowserManager(
            headless=self.config.headless,
            pool_size=self.config.browser_pool_size,
            timeout_ms=self.config.scraper_timeout_ms,
        ) as bm:
            scraper = IndeedScraper(
                bm, rate_limiter, retry_handler, debug=self.config.dev_mode
            )
            return await pipeline.execute(
                scraper,
                keywords,
                locations,
                pages=self.config.pages_per_search,
                experience=experience,
            )

    async def run_full_pipeline(
        self,
        source: str = "naukri",
        keywords: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        experience: str = "",
        **_kwargs,
    ) -> PipelineResult:
        """Dispatch to the requested source scraper and return PipelineResult."""
        keywords = keywords or []
        locations = locations or []
        source = (source or "naukri").lower().strip()

        _logger.info(
            "DevModeRunner starting",
            extra_data={
                "source": source,
                "keywords": keywords,
                "locations": locations,
            },
        )

        if source == "indeed":
            return await self.run_indeed_scraper(
                keywords=keywords, locations=locations, experience=experience
            )
        if source == "naukri":
            return await self.run_naukri_scraper(
                keywords=keywords, locations=locations, experience=experience
            )

        raise ValueError(f"Unknown scraper source: {source!r} (expected naukri|indeed)")


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entrypoint: ``python -m dev_mode.dev_runner``."""
    parser = argparse.ArgumentParser(description="JobHunter scraper (dev mode)")
    parser.add_argument(
        "--source",
        default="naukri",
        choices=["naukri", "indeed"],
        help="Scraper source (default: naukri)",
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["Python Developer"],
        help="Search keywords",
    )
    parser.add_argument(
        "--locations",
        nargs="+",
        default=["Bangalore"],
        help="Search locations",
    )
    parser.add_argument("--experience", default="", help="Optional experience filter")
    args = parser.parse_args(argv)

    runner = DevModeRunner()
    result = asyncio.run(
        runner.run_full_pipeline(
            source=args.source,
            keywords=args.keywords,
            locations=args.locations,
            experience=args.experience,
        )
    )
    print(
        f"Done source={result.source} raw={result.raw_jobs_count} "
        f"final={result.final_jobs_count} duration={result.duration_seconds}s"
    )
    sys.exit(0 if result.errors_count == 0 else 1)


if __name__ == "__main__":
    main()
