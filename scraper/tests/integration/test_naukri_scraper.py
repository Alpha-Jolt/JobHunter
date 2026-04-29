"""Integration tests for NaukriScraper using mock Playwright pages."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.sources.naukri_scraper import NaukriScraper

# Minimal HTML with a valid ItemList JSON-LD block
_MOCK_HTML = """
<html><body>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"ItemList","name":"Python Developer Jobs","numberOfItems":2,"itemListElement":[
  {"@type":"ListItem","position":1,"url":"https://www.naukri.com/job-listings-python-developer-acme-corp-bangalore-2-to-5-years-270426003337","name":"Python Developer","image":"https://img.naukimg.com/logo.gif"},
  {"@type":"ListItem","position":2,"url":"https://www.naukri.com/job-listings-senior-python-developer-beta-ltd-mumbai-5-to-8-years-300326006122","name":"Senior Python Developer","image":"https://img.naukimg.com/logo2.gif"}
]}</script>
</body></html>
"""

_EMPTY_HTML = "<html><body><p>No jobs</p></body></html>"


def _make_mock_browser_manager(html: str):
    bm = MagicMock()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.content = AsyncMock(return_value=html)
    mock_context = AsyncMock()
    mock_context.close = AsyncMock()
    mock_page.context = mock_context
    bm.get_page = AsyncMock(return_value=mock_page)
    return bm


@pytest.mark.asyncio
async def test_naukri_scraper_parses_mock_response():
    bm = _make_mock_browser_manager(_MOCK_HTML)
    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(bm, rl, rh)
    await scraper.initialize()
    jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)

    assert len(jobs) == 2
    assert jobs[0].title == "Python Developer"
    assert jobs[0].source == "naukri"
    assert jobs[1].title == "Senior Python Developer"


@pytest.mark.asyncio
async def test_naukri_scraper_handles_empty_response():
    bm = _make_mock_browser_manager(_EMPTY_HTML)
    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(bm, rl, rh)
    await scraper.initialize()
    jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)

    assert jobs == []
