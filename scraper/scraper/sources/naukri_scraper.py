"""Naukri.com scraper using Playwright + JSON-LD extraction.

The previous HTTP API (POST /api/v5/jobs/search) returns HTTP 301 → homepage.
Naukri now requires a real browser session. Job data is extracted from the
application/ld+json ItemList block embedded in each search results page.
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from scraper.core.browser_manager import BrowserManager
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.base_scraper import BaseScraper

DOMAIN = "www.naukri.com"
BASE_URL = "https://www.naukri.com"

# Regex to extract the ItemList JSON-LD block
_ITEM_LIST_RE = re.compile(
    r'<script type="application/ld\+json">(\{[^<]*"@type"\s*:\s*"ItemList"[^<]*\})</script>',
    re.DOTALL,
)

# Regex to extract job ID from Naukri URL slug
_JOB_ID_RE = re.compile(r"-(\d{12,})$")


class NaukriScraper(BaseScraper):
    """Scrapes Naukri.com using Playwright + JSON-LD page data."""

    def __init__(
        self,
        browser_manager: BrowserManager,
        rate_limiter: RateLimiter,
        retry_handler: RetryHandler,
        debug: bool = False,
    ) -> None:
        super().__init__(rate_limiter, retry_handler, debug)
        self.browser_manager = browser_manager

    async def initialize(self) -> None:
        self.logger.info("NaukriScraper ready")

    async def close(self) -> None:
        pass  # BrowserManager lifecycle managed externally

    def get_source_name(self) -> str:
        return "naukri"

    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        pages: int = 5,
        **kwargs,
    ) -> List[IntermediateJob]:
        results: List[IntermediateJob] = []
        for keyword in keywords:
            for location in locations:
                try:
                    jobs = await self.retry_handler.execute_with_retry(
                        self._scrape_keyword_location,
                        keyword,
                        location,
                        pages,
                    )
                    results.extend(jobs)
                    self.logger.info(
                        "Keyword-location done",
                        extra_data={
                            "keyword": keyword,
                            "location": location,
                            "count": len(jobs),
                        },
                    )
                except Exception as exc:
                    self.logger.error(
                        "Keyword-location failed",
                        extra_data={
                            "keyword": keyword,
                            "location": location,
                            "error": str(exc),
                        },
                        exc_info=True,
                    )
        return results

    async def _scrape_keyword_location(
        self, keyword: str, location: str, pages: int
    ) -> List[IntermediateJob]:
        jobs: List[IntermediateJob] = []
        for page_num in range(1, pages + 1):
            page_jobs = await self._scrape_page(keyword, location, page_num)
            jobs.extend(page_jobs)
            if not page_jobs:
                break
        return jobs

    async def _scrape_page(
        self, keyword: str, location: str, page_num: int
    ) -> List[IntermediateJob]:
        """Scrape one search results page via Playwright and extract JSON-LD."""
        # Build SEO-style URL that Naukri uses
        kw_slug = keyword.lower().replace(" ", "-")
        loc_slug = location.lower().replace(" ", "-")
        url = f"{BASE_URL}/{kw_slug}-jobs-in-{loc_slug}"
        if page_num > 1:
            url += f"-{page_num}"

        await self.rate_limiter.acquire(DOMAIN)
        page: Optional[Page] = None
        try:
            page = await self.browser_manager.get_page("naukri")
            await page.goto(url, timeout=40_000)
            try:
                await page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception:
                pass  # Proceed even if networkidle times out
            await page.wait_for_timeout(2_000)

            content = await page.content()
            jobs = self._extract_from_jsonld(content, keyword, location)

            self.logger.debug(
                "Naukri page scraped",
                extra_data={"url": url, "jobs": len(jobs), "page": page_num},
            )
            return jobs

        except PlaywrightTimeout:
            self.logger.warning("Naukri page timeout", extra_data={"url": url})
            return []
        except Exception as exc:
            self.logger.error(
                "Naukri page error",
                extra_data={"url": url, "error": str(exc)},
                exc_info=True,
            )
            return []
        finally:
            if page:
                await page.context.close()

    def _extract_from_jsonld(
        self, html: str, keyword: str, location: str
    ) -> List[IntermediateJob]:
        """Extract jobs from the application/ld+json ItemList block."""
        import json  # noqa: PLC0415

        jobs: List[IntermediateJob] = []

        # Find all JSON-LD blocks and pick the ItemList one
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
        )
        item_list = None
        for block in blocks:
            try:
                data = json.loads(block)
                if data.get("@type") == "ItemList":
                    item_list = data
                    break
            except json.JSONDecodeError:
                continue

        if not item_list:
            self.logger.warning("No ItemList JSON-LD found on Naukri page")
            return []

        for item in item_list.get("itemListElement", []):
            job = self._parse_item(item)
            if job:
                jobs.append(job)

        return jobs

    def _parse_item(self, item: Dict) -> Optional[IntermediateJob]:
        """Parse a single ItemList entry into an IntermediateJob."""
        start = time.monotonic()
        try:
            url = item.get("url", "")
            title = item.get("name", "")
            if not url or not title:
                return None

            # Extract job ID from URL slug (last numeric segment)
            match = _JOB_ID_RE.search(url)
            job_id = match.group(1) if match else url.split("/")[-1]

            # Parse company/location/experience from URL slug
            slug = url.split("/job-listings-")[-1] if "job-listings-" in url else ""
            company_raw, location_raw, experience_raw = self._parse_slug(slug)

            duration_ms = (time.monotonic() - start) * 1000

            return IntermediateJob(
                source="naukri",
                external_id=job_id,
                raw_url=url,
                title=title,
                company_name=company_raw,
                location_raw=location_raw,
                experience_raw=experience_raw,
                apply_url=url,
                extraction_timestamp=datetime.utcnow(),
                extraction_duration_ms=duration_ms,
                extraction_source="html_parser",
            )
        except Exception as exc:
            self.logger.warning(
                "Item parse failed", extra_data={"error": str(exc)}
            )
            return None

    @staticmethod
    def _parse_slug(slug: str) -> tuple:
        """
        Extract company, location, experience from Naukri URL slug.

        Slug format: {title}-{company}-{locations}-{exp}-years-{id}
        Example: python-developer-tata-consultancy-services-bengaluru-4-to-8-years-300326006122
        """
        # Remove trailing job ID
        slug = _JOB_ID_RE.sub("", slug).strip("-")

        # Experience pattern: "X-to-Y-years" or "X-years"
        exp_match = re.search(r"(\d+-to-\d+-years|\d+-years)", slug)
        experience_raw = exp_match.group(1).replace("-", " ") if exp_match else None
        if exp_match:
            slug = slug[: exp_match.start()].strip("-")

        # Split remaining into parts — heuristic: last 1-3 parts are location
        parts = slug.split("-")
        # Company is typically after the title keywords (first 2-3 words)
        # This is a best-effort parse from the slug
        company_raw = None
        location_raw = None

        if len(parts) > 4:
            # Middle section tends to be company name
            mid = len(parts) // 2
            company_raw = " ".join(p.capitalize() for p in parts[2:mid])
            location_raw = " ".join(p.capitalize() for p in parts[mid:])

        return company_raw, location_raw, experience_raw
