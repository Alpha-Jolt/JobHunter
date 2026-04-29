"""Integration tests for NaukriScraper using mock HTTP responses."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.sources.naukri_scraper import NaukriScraper

_FIXTURE = Path(__file__).parent.parent / "fixtures/mock_json/naukri_api_response.json"


@pytest.mark.asyncio
async def test_naukri_scraper_parses_mock_response():
    mock_data = json.loads(_FIXTURE.read_text())

    mock_response = MagicMock()
    mock_response.json.return_value = mock_data
    mock_response.raise_for_status = MagicMock()

    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(rl, rh)
    await scraper.initialize()

    with patch.object(scraper._session, "post", new=AsyncMock(return_value=mock_response)):
        jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)

    await scraper.close()

    assert len(jobs) == 2
    assert jobs[0].title == "Python Developer"
    assert jobs[0].source == "naukri"
    assert jobs[0].external_id == "naukri_001"
    assert "Python" in jobs[0].skills_required_raw


@pytest.mark.asyncio
async def test_naukri_scraper_handles_empty_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {"jobDetails": []}
    mock_response.raise_for_status = MagicMock()

    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(rl, rh)
    await scraper.initialize()

    with patch.object(scraper._session, "post", new=AsyncMock(return_value=mock_response)):
        jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)

    await scraper.close()
    assert jobs == []
