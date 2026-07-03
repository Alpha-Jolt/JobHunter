"""API reverse engineering extractor — intercepts XHR/fetch calls during Playwright render."""

import logging
from typing import List, Optional

from scraper.sources.career_page.base import BaseCareerExtractor
from scraper.sources.career_page.url_utils import is_job_url

logger = logging.getLogger(__name__)

_PAGE_TIMEOUT = 30_000  # ms
_NETWORK_IDLE_TIMEOUT = 5_000  # ms

# URL path patterns that indicate a jobs data API endpoint
_API_PATH_PATTERNS = [
    "/api/jobs",
    "/jobs.json",
    "/api/positions",
    "/api/openings",
    "/api/vacancies",
    "/graphql",
    "/_next/data",
    "/api/careers",
    "/wp-json",
]

# Keys that suggest a JSON response contains job listings
_JOB_ARRAY_KEYS = [
    "jobs", "postings", "positions", "openings", "vacancies",
    "results", "data", "items", "listings",
]

# Fields that indicate an item is a job listing
_JOB_ITEM_KEYS = frozenset(["title", "description", "location", "applyUrl", "url"])


class APIReverseExtractor(BaseCareerExtractor):
    """Intercepts API calls made during page render to find job data endpoints.

    Uses Playwright to load the career page and capture all XHR/fetch responses.
    If a clean JSON endpoint returning job data is found, it is used directly.
    """

    def get_extraction_method(self) -> str:
        return "api_reverse"

    async def extract(self, company: dict) -> List[dict]:
        """Render the career page and intercept API responses for job data.

        Args:
            company: Company record dict.

        Returns:
            List of raw job field dicts, or empty list if no API endpoint found.
        """
        career_url = company.get("career_page_url")
        if not career_url:
            return []

        api_responses: List[tuple] = []

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="JobHunterBot/1.0",
                    ignore_https_errors=True,
                )
                page = await context.new_page()

                async def handle_response(response):
                    url = response.url.lower()
                    if any(pattern in url for pattern in _API_PATH_PATTERNS):
                        try:
                            content_type = response.headers.get("content-type", "")
                            if "json" in content_type:
                                data = await response.json()
                                api_responses.append((response.url, data))
                        except Exception:
                            pass

                page.on("response", handle_response)

                try:
                    await page.goto(
                        career_url,
                        timeout=_PAGE_TIMEOUT,
                        wait_until="networkidle",
                    )
                except Exception:
                    # networkidle timeout is acceptable — we may have captured responses
                    pass

                await browser.close()

        except Exception as exc:
            logger.debug(
                "API reverse extraction failed",
                extra={"url": career_url, "error": str(exc)},
            )
            return []

        # Parse captured responses for job listings
        for api_url, data in api_responses:
            jobs = self._parse_api_response(data, company, api_url)
            if jobs:
                logger.info(
                    "API reverse extracted jobs",
                    extra={"api_url": api_url, "jobs": len(jobs)},
                )
                return jobs

        return []

    def _parse_api_response(
        self, data: object, company: dict, api_url: str
    ) -> List[dict]:
        """Attempt to extract job listings from a captured API response.

        Args:
            data: Parsed JSON response data.
            company: Company record dict.
            api_url: Source URL of the API response.

        Returns:
            List of raw job dicts, or empty list if structure is not recognised.
        """
        if not isinstance(data, (dict, list)):
            return []

        # If the response is a list, check if items look like jobs
        if isinstance(data, list):
            return self._extract_from_array(data, company)

        # If the response is a dict, look for a jobs array under common keys
        for key in _JOB_ARRAY_KEYS:
            items = data.get(key)
            if isinstance(items, list) and items:
                result = self._extract_from_array(items, company)
                if result:
                    return result

        return []

    def _extract_from_array(self, items: list, company: dict) -> List[dict]:
        """Extract job dicts from a JSON array.

        Args:
            items: List of potential job objects.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        jobs: List[dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            # Check if this item has enough job-like keys
            item_keys = set(str(k).lower() for k in item.keys())
            if not item_keys.intersection({"title", "name", "jobtitle"}):
                continue

            title = (
                item.get("title")
                or item.get("name")
                or item.get("jobTitle")
                or item.get("job_title")
                or ""
            )
            if not title:
                continue

            job_url = (
                item.get("url")
                or item.get("hostedUrl")
                or item.get("applyUrl")
                or item.get("apply_url")
                or item.get("link")
                or company.get("career_page_url", "")
            )
            description = (
                item.get("description")
                or item.get("content")
                or item.get("descriptionPlain")
                or ""
            )
            location = (
                item.get("location")
                or item.get("locationName")
                or item.get("city")
                or ""
            )
            if isinstance(location, dict):
                location = location.get("name", "") or location.get("city", "")

            jobs.append({
                "job_title": str(title).strip(),
                "job_url": str(job_url).strip(),
                "description": str(description).strip(),
                "location": str(location).strip(),
                "ats_platform": company.get("ats_platform", "custom"),
                "extraction_method": "api_reverse",
                "company_id": company.get("company_id"),
            })

        return jobs
