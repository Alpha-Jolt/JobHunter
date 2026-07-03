"""HTML parser extractor — finds job listings from repeating structural patterns."""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag

from scraper.sources.career_page.base import BaseCareerExtractor
from scraper.sources.career_page.url_utils import is_job_url

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 15.0

# Heading tag names likely to contain job titles
_TITLE_TAGS = {"h1", "h2", "h3", "h4", "strong", "b"}

# Minimum number of repeating job-like elements to consider the pattern valid
_MIN_REPEATING = 2


class HTMLExtractor(BaseCareerExtractor):
    """Parses the rendered career page HTML for repeating job listing patterns.

    Strategy:
    1. Fetch the career page (static HTTP — no Playwright)
    2. Identify repeating structural containers (ul/li, div grids, etc.)
    3. Within each candidate container, look for job title + link pairs
    4. Return discovered job URLs as stubs for individual page extraction
    """

    def get_extraction_method(self) -> str:
        return "html_parse"

    async def extract(self, company: dict) -> List[dict]:
        """Parse the career page HTML for job listing patterns.

        Args:
            company: Company record dict.

        Returns:
            List of raw job dicts (stubs with job_url for individual fetch).
        """
        career_url = company.get("career_page_url")
        if not career_url:
            return []

        html = await self._fetch(career_url)
        if not html:
            return []

        jobs = self._parse_jobs(html, career_url, company)
        logger.info(
            "HTML parse extracted",
            extra={"url": career_url, "jobs": len(jobs)},
        )
        return jobs

    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return HTML.

        Args:
            url: Career page URL.

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
            logger.debug("HTML extractor fetch failed", extra={"url": url, "error": str(exc)})
        return None

    def _parse_jobs(self, html: str, base_url: str, company: dict) -> List[dict]:
        """Parse HTML and extract job listings.

        Args:
            html: Raw HTML string.
            base_url: Base URL used to resolve relative links.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        soup = BeautifulSoup(html, "lxml")
        jobs: List[dict] = []

        # Strategy 1: <ul>/<ol> with <li> children
        for list_tag in soup.find_all(["ul", "ol"]):
            items = list_tag.find_all("li", recursive=False)
            if len(items) < _MIN_REPEATING:
                continue
            candidates = self._extract_from_list_items(items, base_url, company)
            if len(candidates) >= _MIN_REPEATING:
                jobs.extend(candidates)
                break

        # Strategy 2: repeating div/article/section blocks with similar classes
        if not jobs:
            jobs = self._extract_from_repeating_divs(soup, base_url, company)

        # Deduplicate by job_url
        seen: set = set()
        unique: List[dict] = []
        for job in jobs:
            url = job.get("job_url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(job)

        return unique

    def _extract_from_list_items(
        self, items: list, base_url: str, company: dict
    ) -> List[dict]:
        """Extract job title + URL from a list of <li> elements.

        Args:
            items: List of BeautifulSoup <li> tags.
            base_url: Base URL for resolving relative hrefs.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        jobs: List[dict] = []
        for item in items:
            if not isinstance(item, Tag):
                continue
            anchor = item.find("a", href=True)
            if not anchor:
                continue
            href = anchor["href"]
            job_url = _resolve_url(base_url, href)
            # Only include URLs that look like job listings or are same-domain
            if not (is_job_url(job_url) or _is_same_domain(base_url, job_url)):
                continue
            # Extract title from heading tags inside the list item
            title = self._extract_title(item) or anchor.get_text(strip=True)
            if not title:
                continue
            jobs.append({
                "job_title": title,
                "job_url": job_url,
                "ats_platform": company.get("ats_platform", "custom"),
                "extraction_method": "html_parse",
                "company_id": company.get("company_id"),
                "_needs_detail_fetch": True,
            })
        return jobs

    def _extract_from_repeating_divs(
        self, soup: BeautifulSoup, base_url: str, company: dict
    ) -> List[dict]:
        """Detect repeating div/article blocks with consistent class names.

        Args:
            soup: Parsed BeautifulSoup object.
            base_url: Base URL for resolving relative hrefs.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        from collections import Counter

        # Count class combinations of block-level elements to find repeating patterns
        class_counts: Counter = Counter()
        for tag in soup.find_all(["div", "article", "section", "li"]):
            classes = tuple(tag.get("class", []))
            if classes and len(classes) <= 5:
                class_counts[classes] += 1

        # Find the most common non-trivial class pattern (≥ min repeating)
        for class_tuple, count in class_counts.most_common(20):
            if count < _MIN_REPEATING:
                break
            # Skip very generic single-word classes
            if len(class_tuple) == 1 and len(class_tuple[0]) <= 3:
                continue

            blocks = soup.find_all(True, class_=list(class_tuple))
            candidates: List[dict] = []
            for block in blocks:
                anchor = block.find("a", href=True)
                if not anchor:
                    continue
                href = anchor["href"]
                job_url = _resolve_url(base_url, href)
                if not (is_job_url(job_url) or _is_same_domain(base_url, job_url)):
                    continue
                title = self._extract_title(block) or anchor.get_text(strip=True)
                if not title:
                    continue
                candidates.append({
                    "job_title": title,
                    "job_url": job_url,
                    "ats_platform": company.get("ats_platform", "custom"),
                    "extraction_method": "html_parse",
                    "company_id": company.get("company_id"),
                    "_needs_detail_fetch": True,
                })

            if len(candidates) >= _MIN_REPEATING:
                return candidates

        return []

    @staticmethod
    def _extract_title(tag: Tag) -> Optional[str]:
        """Extract a job title from heading/strong tags within a block.

        Args:
            tag: BeautifulSoup tag to search.

        Returns:
            Cleaned title string or None.
        """
        for heading_tag in _TITLE_TAGS:
            el = tag.find(heading_tag)
            if el:
                text = el.get_text(strip=True)
                if text and len(text) > 3:
                    return re.sub(r"\s+", " ", text)
        return None


# --- Helpers ----------------------------------------------------------------

def _resolve_url(base_url: str, href: str) -> str:
    """Resolve a relative or absolute href against a base URL."""
    return urljoin(base_url, href)


def _is_same_domain(base_url: str, url: str) -> bool:
    """Return True if url shares the same netloc as base_url."""
    from urllib.parse import urlparse
    try:
        base_netloc = urlparse(base_url).netloc.lstrip("www.")
        url_netloc = urlparse(url).netloc.lstrip("www.")
        return base_netloc == url_netloc
    except Exception:
        return False
