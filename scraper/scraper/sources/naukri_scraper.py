"""Naukri.com API-based scraper."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.extraction.json_parser import JSONExtractor
from scraper.sources.base_scraper import BaseScraper

DOMAIN = "www.naukri.com"
SEARCH_URL = "https://www.naukri.com/api/v5/jobs/search"
DETAIL_URL = "https://www.naukri.com/api/v5/jobs/{job_id}"

_HEADERS = {
    "appid": "109",
    "systemid": "109",
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


class NaukriScraper(BaseScraper):
    """Scrapes job listings from Naukri.com via their internal API."""

    def __init__(
        self,
        rate_limiter: RateLimiter,
        retry_handler: RetryHandler,
        debug: bool = False,
    ) -> None:
        super().__init__(rate_limiter, retry_handler, debug)
        self._session: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        self._session = httpx.AsyncClient(headers=_HEADERS, timeout=15.0)
        self.logger.info("NaukriScraper ready")

    async def close(self) -> None:
        if self._session:
            await self._session.aclose()
            self._session = None

    def get_source_name(self) -> str:
        return "naukri"

    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        experience_years: Optional[List[int]] = None,
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
                        experience_years,
                        pages,
                    )
                    results.extend(jobs)
                    self.logger.info(
                        "Keyword-location done",
                        extra_data={"keyword": keyword, "location": location, "count": len(jobs)},
                    )
                except Exception as exc:
                    self.logger.error(
                        "Keyword-location failed",
                        extra_data={"keyword": keyword, "location": location, "error": str(exc)},
                        exc_info=True,
                    )
        return results

    async def _scrape_keyword_location(
        self,
        keyword: str,
        location: str,
        experience_years: Optional[List[int]],
        pages: int,
    ) -> List[IntermediateJob]:
        jobs: List[IntermediateJob] = []
        for page_num in range(1, pages + 1):
            page_jobs = await self._scrape_page(keyword, location, experience_years, page_num)
            jobs.extend(page_jobs)
            if not page_jobs:
                break
        return jobs

    async def _scrape_page(
        self,
        keyword: str,
        location: str,
        experience_years: Optional[List[int]],
        page_num: int,
    ) -> List[IntermediateJob]:
        await self.rate_limiter.acquire(DOMAIN)

        payload: Dict[str, Any] = {
            "filters": {
                "jobTitle": keyword,
                "cities": location,
                "pageNo": page_num,
                "pageSize": 50,
            }
        }
        if experience_years:
            payload["filters"]["jobExperience"] = experience_years

        try:
            resp = await self._session.post(SEARCH_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as exc:
            self.logger.warning(
                "Naukri API error",
                extra_data={"status": exc.response.status_code, "page": page_num},
            )
            return []
        except Exception as exc:
            self.logger.error(
                "Naukri request failed",
                extra_data={"error": str(exc)},
                exc_info=True,
            )
            return []

        listings = JSONExtractor.extract_array_values(data, "jobDetails") or []
        jobs: List[IntermediateJob] = []
        for listing in listings:
            job = self._parse_listing(listing)
            if job:
                jobs.append(job)
        return jobs

    def _parse_listing(self, listing: Dict[str, Any]) -> Optional[IntermediateJob]:
        start = time.monotonic()
        try:
            job_id = str(JSONExtractor.safe_extract(listing, "jobId", ""))
            if not job_id:
                return None

            title = JSONExtractor.safe_extract(listing, "title", "")
            company = JSONExtractor.safe_extract(listing, "companyName", "")
            location = JSONExtractor.safe_extract(listing, "placeholders.0.label", "")
            salary = JSONExtractor.safe_extract(listing, "salary.label", "")
            experience = JSONExtractor.safe_extract(listing, "experience.label", "")
            description = JSONExtractor.safe_extract(listing, "jobDescription", "")
            job_url = JSONExtractor.safe_extract(
                listing,
                "jdURL",
                f"https://www.naukri.com/job-listings-{job_id}",
            )
            posted_raw = JSONExtractor.safe_extract(listing, "footerPlaceholderLabel", "")

            skills_raw = JSONExtractor.extract_array_values(listing, "tagsAndSkills")
            skills = [s.get("label", "") for s in skills_raw if isinstance(s, dict)]

            duration_ms = (time.monotonic() - start) * 1000

            return IntermediateJob(
                source="naukri",
                external_id=job_id,
                raw_url=job_url,
                title=title,
                company_name=company,
                location_raw=location,
                salary_raw=salary,
                experience_raw=experience,
                description=description,
                posted_date_raw=posted_raw,
                apply_url=job_url,
                skills_required_raw=skills,
                extraction_timestamp=datetime.utcnow(),
                extraction_duration_ms=duration_ms,
                extraction_source="json_api",
            )
        except Exception as exc:
            self.logger.warning("Listing parse failed", extra_data={"error": str(exc)})
            return None
