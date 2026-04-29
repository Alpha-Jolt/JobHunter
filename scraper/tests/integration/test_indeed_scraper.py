"""Integration tests for IndeedScraper using mock Playwright pages."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.indeed_scraper import IndeedScraper


def _make_mock_browser_manager():
    bm = MagicMock()
    bm.get_page = AsyncMock()
    return bm


@pytest.mark.asyncio
async def test_indeed_scraper_returns_empty_on_timeout():
    """IndeedScraper should return [] gracefully on page timeout."""
    from playwright.async_api import TimeoutError as PlaywrightTimeout  # noqa: PLC0415

    bm = _make_mock_browser_manager()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
    mock_page.context = AsyncMock()
    mock_page.context.close = AsyncMock()
    bm.get_page.return_value = mock_page

    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)
    scraper = IndeedScraper(bm, rl, rh)
    await scraper.initialize()

    jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)
    assert jobs == []


@pytest.mark.asyncio
async def test_indeed_get_source_name():
    bm = _make_mock_browser_manager()
    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)
    scraper = IndeedScraper(bm, rl, rh)
    assert scraper.get_source_name() == "indeed"
