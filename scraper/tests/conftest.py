"""Shared pytest fixtures."""

import pytest
import pytest_asyncio

from scraper.core.browser_manager import BrowserManager
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler


@pytest_asyncio.fixture
async def browser_manager():
    async with BrowserManager(headless=True, pool_size=1) as bm:
        yield bm


@pytest.fixture
def rate_limiter():
    return RateLimiter()


@pytest.fixture
def retry_handler():
    return RetryHandler(max_retries=2, base_delay=0.1, max_delay=1.0)
