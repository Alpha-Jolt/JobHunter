"""Worker — executes a single scraper pipeline job (called by scheduler)."""

from typing import List

from scraper.logging_.logger import Logger
from scraper.pipeline.pipeline import ScraperPipeline

_logger = Logger.get_logger(__name__)


async def run_scraper_job(
    pipeline: ScraperPipeline,
    scraper_name: str,
    keywords: List[str],
    locations: List[str],
) -> None:
    """Entry point for scheduled scraper jobs."""
    from scraper.config import config  # noqa: PLC0415
    from scraper.core.browser_manager import BrowserManager  # noqa: PLC0415
    from scraper.core.rate_limiter import RateLimiter  # noqa: PLC0415
    from scraper.core.retry_handler import RetryHandler  # noqa: PLC0415

    _logger.info("Worker starting", extra_data={"source": scraper_name})

    rate_limiter = RateLimiter()
    rate_limiter.set_rate("in.indeed.com", config.indeed_rate_limit)
    rate_limiter.set_rate("www.naukri.com", config.naukri_rate_limit)
    retry_handler = RetryHandler(
        max_retries=config.max_retries,
        base_delay=config.retry_base_delay,
        max_delay=config.retry_max_delay,
    )

    if scraper_name == "indeed":
        async with BrowserManager(
            headless=config.headless,
            pool_size=config.browser_pool_size,
            timeout_ms=config.scraper_timeout_ms,
        ) as bm:
            from scraper.sources.indeed_scraper import IndeedScraper  # noqa: PLC0415

            scraper = IndeedScraper(bm, rate_limiter, retry_handler, debug=config.dev_mode)
            await pipeline.execute(scraper, keywords, locations, pages=config.pages_per_search)

    elif scraper_name == "naukri":
        from scraper.sources.naukri_scraper import NaukriScraper  # noqa: PLC0415

        async with BrowserManager(
            headless=config.headless,
            pool_size=config.browser_pool_size,
            timeout_ms=config.scraper_timeout_ms,
        ) as bm:
            scraper = NaukriScraper(bm, rate_limiter, retry_handler, debug=config.dev_mode)
            await scraper.initialize()
            await pipeline.execute(scraper, keywords, locations, pages=config.pages_per_search)

    else:
        _logger.warning("Unknown scraper", extra_data={"source": scraper_name})
