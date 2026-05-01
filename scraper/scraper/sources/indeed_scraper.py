"""Indeed India scraper using Playwright."""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote_plus

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from scraper.core.browser_manager import BrowserManager
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.base_scraper import BaseScraper

BASE_URL = "https://in.indeed.com/jobs"
DOMAIN = "in.indeed.com"

SELECTORS: Dict[str, str] = {
    "job_cards": ".job_seen_beacon",
    "job_link": "a[data-jk]",
    "job_title": ".jobTitle span",
    "company_name": '[data-testid="company-name"]',
    "location": '[data-testid="text-location"]',
    "salary": ".salary-snippet-container",
    "description": "#jobDescriptionText",
    "job_type_badge": '[data-testid="attribute_snippet_testid"]',
    "posted_date": '[data-testid="myJobsStateDate"]',
}

_SKILL_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "django",
    "flask",
    "spring",
    "angular",
    "vue",
    "mongodb",
    "postgresql",
    "redis",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "data analysis",
    "excel",
    "power bi",
    "tableau",
]

_CF_WAIT_MS = 3_000
_CF_MAX_POLLS = 5


class IndeedScraper(BaseScraper):
    """Scrapes job listings from Indeed India."""

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
        self.logger.info("IndeedScraper ready")

    async def close(self) -> None:
        pass  # BrowserManager lifecycle managed externally

    def get_source_name(self) -> str:
        return "indeed"

    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        pages: int = 5,
        **kwargs,
    ) -> List[IntermediateJob]:
        """Scrape all keyword × location combinations."""
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
        for page_num in range(pages):
            offset = page_num * 10
            page_jobs = await self._scrape_page(keyword, location, offset)
            jobs.extend(page_jobs)
            if not page_jobs:
                break  # No more results
        return jobs

    async def _scrape_page(
        self, keyword: str, location: str, offset: int
    ) -> List[IntermediateJob]:
        url = (
            f"{BASE_URL}"
            f"?q={quote_plus(keyword)}"
            f"&l={quote_plus(location)}"
            f"&start={offset}"
        )
        await self.rate_limiter.acquire(DOMAIN)

        page: Optional[Page] = None
        try:
            page = await self.browser_manager.get_page("indeed")
            await page.goto(
                url, timeout=30_000, wait_until="domcontentloaded"
            )
            # Wait for Cloudflare challenge to resolve (up to 15 s)
            for _ in range(_CF_MAX_POLLS):
                title = await page.title()
                if "just a moment" not in title.lower():
                    break
                await page.wait_for_timeout(_CF_WAIT_MS)
            else:
                self.logger.warning(
                    "Indeed blocked by Cloudflare",
                    extra_data={"url": url},
                )
                return []

            try:
                await page.wait_for_load_state(
                    "networkidle", timeout=10_000
                )
            except Exception:
                pass
            await page.wait_for_timeout(2_000)

            await self._scroll_to_load_jobs(page)

            cards = await page.query_selector_all(SELECTORS["job_cards"])
            self.logger.debug(
                "Cards found",
                extra_data={"url": url, "count": len(cards)},
            )
            jobs: List[IntermediateJob] = []
            for card in cards:
                try:
                    job = await self._extract_job_from_card(page, card)
                    if job:
                        jobs.append(job)
                except Exception as exc:
                    self.logger.warning(
                        "Card extraction failed",
                        extra_data={"error": str(exc)},
                    )

            return jobs
        except PlaywrightTimeout:
            self.logger.warning("Page timeout", extra_data={"url": url})
            return []
        finally:
            if page:
                await page.context.close()

    async def _extract_job_from_card(
        self, list_page: Page, card
    ) -> Optional[IntermediateJob]:
        start = time.monotonic()

        link_el = await card.query_selector(SELECTORS["job_link"])
        if not link_el:
            return None

        job_key = await link_el.get_attribute("data-jk")
        if not job_key:
            return None

        job_url = f"https://in.indeed.com/viewjob?jk={job_key}"

        title_el = await card.query_selector(SELECTORS["job_title"])
        title = (
            (await title_el.inner_text()).strip() if title_el else None
        )

        company_el = await card.query_selector(SELECTORS["company_name"])
        company = (
            (await company_el.inner_text()).strip()
            if company_el
            else None
        )

        location_el = await card.query_selector(SELECTORS["location"])
        location = (
            (await location_el.inner_text()).strip()
            if location_el
            else None
        )

        salary_el = await card.query_selector(SELECTORS["salary"])
        salary = (
            (await salary_el.inner_text()).strip() if salary_el else None
        )

        details = await self._get_full_job_details(job_url)
        duration_ms = (time.monotonic() - start) * 1000

        return IntermediateJob(
            source="indeed",
            external_id=job_key,
            raw_url=job_url,
            title=title,
            company_name=company,
            location_raw=location,
            salary_raw=salary,
            description=(
                details.get("description") if details else None
            ),
            job_type_raw=(
                details.get("job_type") if details else None
            ),
            posted_date_raw=(
                details.get("posted_date") if details else None
            ),
            apply_url=job_url,
            skills_required_raw=self._extract_skills(
                details.get("description", "") if details else ""
            ),
            extraction_timestamp=datetime.utcnow(),
            extraction_duration_ms=duration_ms,
            extraction_source="html_parser",
        )

    async def _get_full_job_details(
        self, job_url: str
    ) -> Optional[Dict]:
        await self.rate_limiter.acquire(DOMAIN)
        page: Optional[Page] = None
        try:
            page = await self.browser_manager.get_page("indeed")
            await page.goto(
                job_url, timeout=30_000, wait_until="domcontentloaded"
            )
            # Wait for Cloudflare challenge to resolve (up to 12 s)
            for _ in range(_CF_MAX_POLLS - 1):
                title = await page.title()
                if "just a moment" not in title.lower():
                    break
                await page.wait_for_timeout(_CF_WAIT_MS)
            else:
                return None

            try:
                await page.wait_for_load_state(
                    "networkidle", timeout=10_000
                )
            except Exception:
                pass
            await page.wait_for_timeout(1_500)

            desc_el = await page.query_selector(SELECTORS["description"])
            description = (
                (await desc_el.inner_text()).strip() if desc_el else ""
            )

            posted_el = await page.query_selector(
                SELECTORS["posted_date"]
            )
            posted_date = (
                (await posted_el.inner_text()).strip()
                if posted_el
                else None
            )

            badge_els = await page.query_selector_all(
                SELECTORS["job_type_badge"]
            )
            job_type = None
            for el in badge_els:
                text = (await el.inner_text()).strip().lower()
                if any(
                    kw in text
                    for kw in ("full", "part", "contract", "intern", "temp")
                ):
                    job_type = text
                    break

            return {
                "description": description,
                "posted_date": posted_date,
                "job_type": job_type,
            }
        except Exception as exc:
            self.logger.warning(
                "Detail fetch failed",
                extra_data={"url": job_url, "error": str(exc)},
            )
            return None
        finally:
            if page:
                await page.context.close()

    @staticmethod
    async def _scroll_to_load_jobs(page: Page) -> None:
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await page.wait_for_timeout(500)

    @staticmethod
    def _extract_skills(description: str) -> List[str]:
        lower = description.lower()
        return [
            kw for kw in _SKILL_KEYWORDS
            if re.search(r"\b" + re.escape(kw) + r"\b", lower)
        ]
