"""Career page router — routes companies to the correct extraction strategy."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from scraper.sources.career_page.base import BaseCareerExtractor
from scraper.sources.career_page.change_detector import ChangeDetector
from scraper.sources.career_page.extractors.api_reverse_extractor import APIReverseExtractor
from scraper.sources.career_page.extractors.ats_api_extractor import ATSApiExtractor
from scraper.sources.career_page.extractors.html_extractor import HTMLExtractor
from scraper.sources.career_page.extractors.json_ld_extractor import JSONLDExtractor
from scraper.sources.career_page.extractors.playwright_extractor import PlaywrightExtractor
from scraper.sources.career_page.extractors.sitemap_extractor import SitemapExtractor
from scraper.sources.career_page.job_cleaner import JobCleanerPipeline
from scraper.sources.career_page.job_page_extractor import JobPageExtractor
from scraper.sources.career_page.url_utils import (
    compute_content_hash,
    compute_url_hash,
    normalize_job_url,
)
from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker

logger = logging.getLogger(__name__)

# ATS platforms with public free-tier APIs — always try API first
_ATS_API_PLATFORMS = {"greenhouse", "lever", "ashby"}


class CareerPageRouter:
    """Routes a company to the correct job extraction strategy.

    Extraction cascade (first success wins):
    1. ATS API (Greenhouse, Lever, Ashby) — if ats_platform is known
    2. JSON-LD structured data
    3. XML Sitemap
    4. API reverse engineering (XHR interception)
    5. HTML pattern parsing
    6. Playwright full render (last resort)

    For strategies 3–6 that return URL stubs (_needs_detail_fetch=True),
    each job URL is individually fetched for full detail extraction.

    Args:
        robots_checker: Shared RobotsChecker instance.
        cleaner: Job cleaner pipeline instance.
        change_detector: Change detector instance.
    """

    def __init__(
        self,
        robots_checker: Optional[RobotsChecker] = None,
        cleaner: Optional[JobCleanerPipeline] = None,
        change_detector: Optional[ChangeDetector] = None,
    ) -> None:
        self._robots_checker = robots_checker or RobotsChecker()
        self._cleaner = cleaner or JobCleanerPipeline()
        self._change_detector = change_detector or ChangeDetector()
        self._job_page_extractor = JobPageExtractor()

        # Extractor instances
        self._ats_api = ATSApiExtractor()
        self._json_ld = JSONLDExtractor()
        self._sitemap = SitemapExtractor()
        self._api_reverse = APIReverseExtractor()
        self._html = HTMLExtractor()
        self._playwright = PlaywrightExtractor()

    async def extract_jobs(self, company: dict) -> List[dict]:
        """Extract all job listings for a given company.

        Args:
            company: Company record dict with at minimum:
                apex_domain, career_page_url, ats_platform, company_id.

        Returns:
            List of cleaned, fully-populated job field dicts ready for storage.
        """
        apex_domain = company.get("apex_domain", "")
        career_url = company.get("career_page_url", "")

        if not career_url:
            logger.debug(
                "No career page URL — skipping",
                extra={"domain": apex_domain},
            )
            return []

        # robots.txt check before any request
        if not await self._robots_checker.is_allowed(apex_domain, "/careers"):
            logger.info(
                "robots.txt blocked career page scrape",
                extra={"domain": apex_domain},
            )
            return []

        raw_jobs = await self._run_extraction_cascade(company)
        if not raw_jobs:
            return []

        # Resolve URL stubs that need individual page fetching
        resolved_jobs = await self._resolve_stubs(raw_jobs, company)

        # Clean all extracted jobs
        cleaned_jobs = []
        for raw in resolved_jobs:
            try:
                cleaned = self._cleaner.clean(raw)
                if cleaned is None:
                    # Title failed garbage validation — skip this job
                    continue
                enriched = self._enrich_with_metadata(cleaned, company)
                cleaned_jobs.append(enriched)
            except Exception as exc:
                logger.debug(
                    "Job cleaning failed",
                    extra={"error": str(exc), "job_url": raw.get("job_url")},
                )

        logger.info(
            "Career page extraction complete",
            extra={
                "domain": apex_domain,
                "jobs": len(cleaned_jobs),
            },
        )
        return cleaned_jobs

    async def _run_extraction_cascade(self, company: dict) -> List[dict]:
        """Try each extraction strategy in priority order.

        Args:
            company: Company record dict.

        Returns:
            List of raw job dicts from the first successful strategy.
        """
        ats = company.get("ats_platform", "none")
        strategies: List[BaseCareerExtractor] = []

        # ATS API first for supported platforms
        if ats in _ATS_API_PLATFORMS:
            strategies.append(self._ats_api)

        # Then general cascade
        strategies.extend([
            self._json_ld,
            self._sitemap,
            self._api_reverse,
            self._html,
            self._playwright,
        ])

        for extractor in strategies:
            try:
                jobs = await extractor.extract(company)
                if jobs:
                    logger.debug(
                        "Extraction succeeded",
                        extra={
                            "method": extractor.get_extraction_method(),
                            "domain": company.get("apex_domain"),
                            "jobs": len(jobs),
                        },
                    )
                    return jobs
            except Exception as exc:
                logger.debug(
                    "Extractor failed",
                    extra={
                        "method": extractor.get_extraction_method(),
                        "error": str(exc),
                    },
                )

        return []

    async def _resolve_stubs(
        self, raw_jobs: List[dict], company: dict
    ) -> List[dict]:
        """Fetch individual job pages for URL stubs.

        Args:
            raw_jobs: List of raw job dicts, some may have _needs_detail_fetch=True.
            company: Company record dict.

        Returns:
            List of raw job dicts with full details.
        """
        resolved: List[dict] = []

        for job in raw_jobs:
            if not job.get("_needs_detail_fetch"):
                resolved.append(job)
                continue

            job_url = job.get("job_url", "")
            if not job_url:
                continue

            # robots.txt check for each job page path
            from urllib.parse import urlparse
            path = urlparse(job_url).path or "/"
            apex = company.get("apex_domain", "")
            if not await self._robots_checker.is_allowed(apex, path):
                logger.debug(
                    "robots.txt blocked job page",
                    extra={"url": job_url},
                )
                continue

            # Carry the extraction method from the parent strategy
            company_with_method = dict(company)
            company_with_method["_extraction_method"] = job.get("extraction_method", "html_parse")

            detail = await self._job_page_extractor.extract(job_url, company_with_method)
            if detail:
                resolved.append(detail)

        return resolved

    def _enrich_with_metadata(self, cleaned: dict, company: dict) -> dict:
        """Add computed metadata fields to a cleaned job dict.

        Adds: url_hash, content_hash, scraped_at, last_seen_at,
        status, source_channel, and company_id.

        Args:
            cleaned: Cleaned job dict from JobCleanerPipeline.
            company: Company record dict.

        Returns:
            Job dict enriched with metadata fields.
        """
        job_url = cleaned.get("job_url", "")
        normalized_url = normalize_job_url(job_url)
        url_hash = compute_url_hash(normalized_url)
        content_hash = compute_content_hash(
            cleaned.get("job_title", ""),
            cleaned.get("description", ""),
        )
        now = datetime.now(timezone.utc)

        enriched = dict(cleaned)
        enriched.update({
            "career_job_id": str(uuid.uuid4()),
            "company_id": company.get("company_id"),
            "url_hash": url_hash,
            "content_hash": content_hash,
            "scraped_at": now.isoformat(),
            "last_seen_at": now.isoformat(),
            "status": "raw",
            "source_channel": "career_page",
        })

        # Set apply_email from company career emails if not already present
        if not enriched.get("apply_email"):
            career_emails = company.get("career_emails", [])
            if career_emails:
                enriched["apply_email"] = career_emails[0]

        return enriched

    def mark_closed_jobs(
        self,
        existing_url_hashes: set,
        seen_url_hashes: set,
    ) -> set:
        """Return the set of URL hashes that should be marked as closed.

        Jobs that existed on the previous crawl but were not seen in the
        current crawl are considered closed.

        Args:
            existing_url_hashes: All known url_hash values for the company.
            seen_url_hashes: url_hash values seen in the current crawl.

        Returns:
            Set of url_hash strings to mark as closed.
        """
        return existing_url_hashes - seen_url_hashes
