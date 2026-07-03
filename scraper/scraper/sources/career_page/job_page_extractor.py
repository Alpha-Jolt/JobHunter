"""Individual job page extractor — fetches and parses a single job detail page."""

import logging
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from scraper.sources.career_page.extractors.json_ld_extractor import JSONLDExtractor

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 15.0


class JobPageExtractor:
    """Extracts job details from an individual job listing page.

    Strategy (in priority order):
    1. JSON-LD JobPosting structured data
    2. HTML fallback — extracts title from heading, description from body

    Used for jobs discovered via sitemap, HTML parsing, or Playwright render
    where only the URL is known and details must be fetched from the job page.
    """

    def __init__(self) -> None:
        self._json_ld_extractor = JSONLDExtractor()

    async def extract(self, job_url: str, company: dict) -> Optional[dict]:
        """Fetch a job detail page and extract all available fields.

        Args:
            job_url: Direct URL to the job listing page.
            company: Company record dict.

        Returns:
            Raw job field dict, or None if extraction fails.
        """
        html = await self._fetch(job_url)
        if not html:
            return None

        # Try JSON-LD first
        jobs = self._json_ld_extractor._parse_json_ld(html, company)
        if jobs:
            job = jobs[0]
            job["job_url"] = job_url  # ensure URL is the canonical page URL
            return job

        # Fall back to HTML extraction
        return self._parse_html_fallback(html, job_url, company)

    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch the job detail page.

        Args:
            url: Job page URL.

        Returns:
            HTML string or None on failure.
        """
        try:
            async with httpx.AsyncClient(
                timeout=_HTTP_TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": "JobHunterBot/1.0"},
            ) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text
        except Exception as exc:
            logger.debug(
                "Job page fetch failed",
                extra={"url": url, "error": str(exc)},
            )
        return None

    def _parse_html_fallback(
        self, html: str, job_url: str, company: dict
    ) -> Optional[dict]:
        """Extract job title and description from HTML using heuristics.

        Args:
            html: Raw HTML string.
            job_url: Source URL of the job page.
            company: Company record dict.

        Returns:
            Raw job dict or None if no title is found.
        """
        soup = BeautifulSoup(html, "lxml")

        # Title: try h1 first, then h2, then <title> tag
        title = ""
        for tag_name in ("h1", "h2", "h3"):
            el = soup.find(tag_name)
            if el:
                title = re.sub(r"\s+", " ", el.get_text()).strip()
                if title and len(title) > 3:
                    break

        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().split("|")[0].split("-")[0].strip()

        if not title:
            return None

        # Description: largest text block on the page (main/article or body)
        description = ""
        for container in ("main", "article", "section", "body"):
            el = soup.find(container)
            if el:
                description = re.sub(r"\s+", " ", el.get_text(separator=" ")).strip()
                if len(description) > 100:
                    break

        return {
            "job_title": title,
            "job_url": job_url,
            "description": description,
            "location": "",
            "ats_platform": company.get("ats_platform", "custom"),
            "extraction_method": company.get("_extraction_method", "html_parse"),
            "company_id": company.get("company_id"),
        }
