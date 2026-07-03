"""XML sitemap extractor — discovers job URLs from sitemap.xml."""

import logging
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from scraper.sources.career_page.base import BaseCareerExtractor
from scraper.sources.career_page.url_utils import is_job_url

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 15.0

# Sitemap filenames that commonly contain job listings
_JOB_SITEMAP_KEYWORDS = ["job", "career", "opening", "position", "vacancy"]


class SitemapExtractor(BaseCareerExtractor):
    """Extracts job URLs from XML sitemaps.

    Handles:
    - Root sitemap.xml
    - Sitemap index files with child sitemaps named after careers/jobs
    - Direct <loc> entries matching job URL patterns
    """

    def get_extraction_method(self) -> str:
        return "sitemap"

    async def extract(self, company: dict) -> List[dict]:
        """Discover job URLs from the company domain's sitemap.

        Returns job URL stubs (job_url + company metadata) that the router
        then passes to the individual job page extractor to fill in details.

        Args:
            company: Company record dict.

        Returns:
            List of raw job dicts containing at minimum job_url and company_id.
        """
        apex_domain = company.get("apex_domain", "")
        if not apex_domain:
            return []

        base_url = f"https://{apex_domain}"
        sitemap_url = base_url + "/sitemap.xml"

        job_urls = await self._collect_job_urls(sitemap_url, base_url)
        if not job_urls:
            return []

        jobs = [
            {
                "job_url": url,
                "ats_platform": company.get("ats_platform", "custom"),
                "extraction_method": "sitemap",
                "company_id": company.get("company_id"),
                "_needs_detail_fetch": True,  # signal to router to fetch individual page
            }
            for url in job_urls
        ]
        logger.info(
            "Sitemap extracted job URLs",
            extra={"domain": apex_domain, "urls": len(jobs)},
        )
        return jobs

    async def _collect_job_urls(self, sitemap_url: str, base_url: str) -> List[str]:
        """Fetch sitemap and collect job listing URLs.

        Args:
            sitemap_url: URL of the root sitemap.xml.
            base_url: Base URL with scheme for the domain.

        Returns:
            List of job page URL strings.
        """
        xml = await self._fetch(sitemap_url)
        if not xml:
            return []

        soup = BeautifulSoup(xml, "lxml-xml")
        job_urls: List[str] = []

        # Check if this is a sitemap index
        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            for tag in sitemap_tags:
                loc = tag.find("loc")
                if not loc:
                    continue
                child_url = loc.text.strip()
                child_name = child_url.lower()
                if any(kw in child_name for kw in _JOB_SITEMAP_KEYWORDS):
                    child_xml = await self._fetch(child_url)
                    if child_xml:
                        child_urls = self._extract_locs(child_xml)
                        job_urls.extend(child_urls)

        # Also scan <loc> entries in the root sitemap directly
        root_locs = self._extract_locs(xml)
        job_urls.extend(root_locs)

        # Deduplicate
        seen: set = set()
        unique: List[str] = []
        for url in job_urls:
            if url not in seen:
                seen.add(url)
                unique.append(url)

        return unique

    def _extract_locs(self, xml: str) -> List[str]:
        """Extract <loc> URLs that match job URL patterns.

        Args:
            xml: Raw XML string.

        Returns:
            List of job URL strings.
        """
        soup = BeautifulSoup(xml, "lxml-xml")
        urls: List[str] = []
        for loc_tag in soup.find_all("loc"):
            url = loc_tag.text.strip()
            if is_job_url(url):
                urls.append(url)
        return urls

    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return text content.

        Args:
            url: URL to fetch.

        Returns:
            Response text or None on failure.
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
            logger.debug("Sitemap fetch failed", extra={"url": url, "error": str(exc)})
        return None
