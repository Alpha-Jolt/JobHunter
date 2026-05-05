"""Integration tests for NaukriScraper using mock Playwright pages."""

import re
from unittest.mock import AsyncMock, MagicMock

import pytest

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.sources.naukri_scraper import NaukriScraper

# Search results page with ItemList JSON-LD
_LISTING_HTML = """
<html><body>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"ItemList","name":"Python Developer Jobs","numberOfItems":2,"itemListElement":[
  {"@type":"ListItem","position":1,"url":"https://www.naukri.com/job-listings-python-developer-acme-corp-bangalore-2-to-5-years-270426003337","name":"Python Developer"},
  {"@type":"ListItem","position":2,"url":"https://www.naukri.com/job-listings-senior-python-developer-beta-ltd-mumbai-5-to-8-years-300326006122","name":"Senior Python Developer"}
]}</script>
</body></html>
"""

# Job detail page with JobPosting JSON-LD
_DETAIL_HTML = """
<html><body>
<script type="application/ld+json">{"@context":"http://schema.org","@type":"JobPosting",
  "title":"Python Developer","description":"<p>We need a Python developer.</p>",
  "datePosted":"2026-04-20","employmentType":"Full Time",
  "hiringOrganization":{"@type":"Organization","name":"Acme Corp"},
  "jobLocation":{"@type":"Place","address":{"@type":"PostalAddress","addressLocality":["Bangalore"]}},
  "baseSalary":{"@type":"MonetaryAmount","currency":"INR","value":{"@type":"QuantitativeValue","value":"8-12 Lacs","unitText":"P.A."}},
  "experienceRequirements":{"@type":"OccupationalExperienceRequirements","monthsOfExperience":"24"},
  "skills":"Python, Django, REST API"
}</script>
</body></html>
"""

_EMPTY_HTML = "<html><body><p>No jobs</p></body></html>"


def _make_mock_bm(listing_html: str, detail_html: str):
    """Return a BrowserManager mock that serves listing then detail pages."""

    async def get_page(source):
        # Listing page
        listing_page = AsyncMock()
        listing_page.goto = AsyncMock()
        listing_page.wait_for_load_state = AsyncMock()
        listing_page.wait_for_timeout = AsyncMock()
        listing_page.content = AsyncMock(return_value=listing_html)

        # Detail page (returned by context.new_page())
        detail_page = AsyncMock()
        detail_page.goto = AsyncMock()
        detail_page.wait_for_load_state = AsyncMock()
        detail_page.wait_for_timeout = AsyncMock()
        detail_page.content = AsyncMock(return_value=detail_html)
        detail_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=detail_page)
        listing_page.context = mock_context

        return listing_page

    bm = MagicMock()
    bm.get_page = get_page
    return bm


@pytest.mark.asyncio
async def test_naukri_scraper_parses_mock_response():
    bm = _make_mock_bm(_LISTING_HTML, _DETAIL_HTML)
    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(bm, rl, rh)
    await scraper.initialize()
    jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)

    assert len(jobs) == 2
    assert jobs[0].title == "Python Developer"
    assert jobs[0].source == "naukri"
    assert jobs[0].description is not None
    assert "Python developer" in jobs[0].description
    assert jobs[0].salary_raw == "INR 8-12 Lacs P.A."
    assert jobs[0].experience_raw == "2 years"
    assert "Python" in jobs[0].skills_required_raw


@pytest.mark.asyncio
async def test_naukri_scraper_handles_empty_response():
    bm = _make_mock_bm(_EMPTY_HTML, _EMPTY_HTML)
    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(bm, rl, rh)
    await scraper.initialize()
    jobs = await scraper.scrape(["Python"], ["Bangalore"], pages=1)

    assert jobs == []


@pytest.mark.asyncio
async def test_naukri_experience_filter_fresher():
    """Fresher filter should exclude jobs requiring >2 years experience."""
    bm = _make_mock_bm(_LISTING_HTML, _DETAIL_HTML)
    rl = RateLimiter()
    rh = RetryHandler(max_retries=0)

    scraper = NaukriScraper(bm, rl, rh)
    await scraper.initialize()
    jobs_fresher = await scraper.scrape(["Python"], ["Bangalore"], pages=1, experience="fresher")

    for j in jobs_fresher:
        if j.experience_raw:
            nums = re.findall(r"\d+", j.experience_raw)
            if nums:
                assert int(nums[0]) <= 2, f"Job {j.title} exp={j.experience_raw} exceeded fresher max"
