"""Naukri.com scraper using Playwright + JSON-LD extraction.

Search results: ItemList JSON-LD -> job URLs
Job details: JobPosting JSON-LD -> full data (description, salary, etc.)
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from scraper.core.browser_manager import BrowserManager
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.base_scraper import BaseScraper

DOMAIN = "www.naukri.com"
BASE_URL = "https://www.naukri.com"

_JOB_ID_RE = re.compile(r"-(\d{12,})$")

# Experience level → (min_years, max_years) for post-scrape filtering
_EXPERIENCE_FILTER: Dict[str, Tuple[int, int]] = {
    "fresher": (0, 2),
    "mid": (3, 7),
    "senior": (8, 99),
}


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
        pass

    def get_source_name(self) -> str:
        return "naukri"

    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        pages: int = 5,
        experience: Optional[str] = None,
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
                        experience,
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
        self,
        keyword: str,
        location: str,
        pages: int,
        experience: Optional[str],
    ) -> List[IntermediateJob]:
        jobs: List[IntermediateJob] = []
        for page_num in range(1, pages + 1):
            page_jobs = await self._scrape_page(keyword, location, page_num, experience)
            jobs.extend(page_jobs)
            if not page_jobs:
                break
        return jobs

    async def _scrape_page(
        self,
        keyword: str,
        location: str,
        page_num: int,
        experience: Optional[str],
    ) -> List[IntermediateJob]:
        """Scrape one search results page and fetch details for each job."""
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
                pass
            await page.wait_for_timeout(2_000)

            content = await page.content()
            job_urls = self._extract_job_urls(content)

            self.logger.debug(
                "Naukri listing page",
                extra_data={
                    "url": url,
                    "job_urls": len(job_urls),
                    "page": page_num,
                },
            )

            # Reuse same browser context for all detail pages
            # (avoids resource exhaustion)
            context = page.context
            jobs: List[IntermediateJob] = []
            for job_url in job_urls:
                job = await self._fetch_job_detail_in_context(context, job_url)
                if job:
                    jobs.append(job)

            # Apply experience filter
            if experience and experience in _EXPERIENCE_FILTER:
                jobs = self._filter_by_experience(jobs, experience)

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

    def _extract_job_urls(self, html: str) -> List[str]:
        """Extract job detail URLs from the ItemList JSON-LD block."""
        import json  # noqa: PLC0415

        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        for block in blocks:
            try:
                data = json.loads(block)
                if data.get("@type") == "ItemList":
                    return [
                        item.get("url", "")
                        for item in data.get("itemListElement", [])
                        if item.get("url")
                    ]
            except json.JSONDecodeError:
                continue

        self.logger.warning("No ItemList JSON-LD found on Naukri page")
        return []

    async def _fetch_job_detail_in_context(
        self, context, job_url: str
    ) -> Optional[IntermediateJob]:
        """Fetch a job detail page reusing an existing browser context."""
        await self.rate_limiter.acquire(DOMAIN)
        detail_page = None
        start = time.monotonic()
        try:
            detail_page = await context.new_page()
            await detail_page.goto(job_url, timeout=40_000)
            try:
                await detail_page.wait_for_load_state("networkidle", timeout=12_000)
            except Exception:
                pass
            await detail_page.wait_for_timeout(1_000)

            content = await detail_page.content()
            return self._parse_job_posting(content, job_url, time.monotonic() - start)

        except Exception as exc:
            self.logger.warning(
                "Job detail fetch failed",
                extra_data={"url": job_url, "error": str(exc)},
            )
            return None
        finally:
            if detail_page:
                await detail_page.close()

    def _parse_job_posting(
        self, html: str, job_url: str, duration_s: float
    ) -> Optional[IntermediateJob]:
        """Extract IntermediateJob from JobPosting JSON-LD on a detail page."""
        import json  # noqa: PLC0415

        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        posting = None
        for block in blocks:
            try:
                data = json.loads(block)
                if data.get("@type") == "JobPosting":
                    posting = data
                    break
            except json.JSONDecodeError:
                continue

        if not posting:
            # Fallback: build minimal record from URL slug
            return self._fallback_from_url(job_url, duration_s)

        match = _JOB_ID_RE.search(job_url)
        job_id = match.group(1) if match else job_url.split("/")[-1]

        # Company
        org = posting.get("hiringOrganization") or {}
        company = org.get("name") if isinstance(org, dict) else None

        # Location
        loc_data = posting.get("jobLocation") or {}
        addr = loc_data.get("address", {}) if isinstance(loc_data, dict) else {}
        localities = addr.get("addressLocality", []) if isinstance(addr, dict) else []
        location_raw = ", ".join(localities) if isinstance(localities, list) else str(localities)

        # Salary — check baseSalary first, then text alternatives
        salary_raw = self._extract_salary(posting)

        # Experience in months → "X years"
        exp_data = posting.get("experienceRequirements") or {}
        months = exp_data.get("monthsOfExperience") if isinstance(exp_data, dict) else None
        experience_raw = None
        if months:
            try:
                years = int(months) // 12
                experience_raw = f"{years} years"
            except (ValueError, TypeError):
                experience_raw = str(months)

        # Description — strip HTML tags
        description_html = posting.get("description", "")
        description = (
            re.sub(r"<[^>]+>", " ", description_html).strip() if description_html else None
        )

        # Skills
        skills_raw_val = posting.get("skills", "")
        if isinstance(skills_raw_val, str):
            skills = [s.strip() for s in skills_raw_val.split(",") if s.strip()]
        elif isinstance(skills_raw_val, list):
            skills = [str(s).strip() for s in skills_raw_val if s]
        else:
            skills = []

        # Job type
        job_type_raw = posting.get("employmentType", "")

        # Date posted
        posted_date_raw = posting.get("datePosted", "")

        return IntermediateJob(
            source="naukri",
            external_id=job_id,
            raw_url=job_url,
            title=posting.get("title", ""),
            company_name=company,
            location_raw=location_raw or None,
            salary_raw=salary_raw,
            experience_raw=experience_raw,
            job_type_raw=job_type_raw or None,
            description=description,
            posted_date_raw=posted_date_raw or None,
            apply_url=job_url,
            skills_required_raw=skills,
            extraction_timestamp=datetime.utcnow(),
            extraction_duration_ms=duration_s * 1000,
            extraction_source="html_parser",
        )

    @staticmethod
    def _extract_salary(posting: Dict) -> Optional[str]:
        """Extract salary string from JobPosting, trying multiple fields."""
        base = posting.get("baseSalary")
        if isinstance(base, dict):
            val = base.get("value", {})
            if isinstance(val, dict):
                amount = val.get("value", "")
                unit = val.get("unitText", "")
                currency = base.get("currency", "INR")
                if amount and str(amount).lower() not in (
                    "not disclosed",
                    "not mentioned",
                    "",
                ):
                    return f"{currency} {amount} {unit}".strip()
        # Alternate: check estimatedSalary
        est = posting.get("estimatedSalary")
        if isinstance(est, dict):
            val = est.get("value", {})
            if isinstance(val, dict):
                mn = val.get("minValue")
                mx = val.get("maxValue")
                unit = val.get("unitText", "")
                currency = est.get("currency", "INR")
                if mn or mx:
                    return f"{currency} {mn}-{mx} {unit}".strip()
        return None

    def _fallback_from_url(self, job_url: str, duration_s: float) -> Optional[IntermediateJob]:
        """Minimal record from URL slug when JSON-LD is unavailable."""
        match = _JOB_ID_RE.search(job_url)
        job_id = match.group(1) if match else job_url.split("/")[-1]
        slug = job_url.split("/job-listings-")[-1] if "job-listings-" in job_url else ""
        slug = _JOB_ID_RE.sub("", slug).strip("-")

        exp_match = re.search(r"(\d+)-to-(\d+)-years", slug)
        experience_raw = f"{exp_match.group(1)}-{exp_match.group(2)} years" if exp_match else None

        return IntermediateJob(
            source="naukri",
            external_id=job_id,
            raw_url=job_url,
            experience_raw=experience_raw,
            apply_url=job_url,
            extraction_timestamp=datetime.utcnow(),
            extraction_duration_ms=duration_s * 1000,
            extraction_source="html_parser",
        )

    @staticmethod
    def _filter_by_experience(
        jobs: List[IntermediateJob], experience: str
    ) -> List[IntermediateJob]:
        """Filter jobs to match the requested experience level."""
        min_y, max_y = _EXPERIENCE_FILTER[experience]
        filtered = []
        for job in jobs:
            exp_raw = job.experience_raw or ""
            nums = re.findall(r"\d+", exp_raw)
            if not nums:
                # No experience info — only include for fresher (open to all)
                if experience == "fresher":
                    filtered.append(job)
                continue
            job_min = int(nums[0])
            if job_min <= max_y:
                filtered.append(job)
        return filtered
