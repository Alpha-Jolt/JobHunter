"""NASSCOM member directory crawler — imports established Indian tech company domains.

NASSCOM (National Association of Software and Service Companies) publishes a
public member directory at nasscom.in. Members are established, actively-hiring
Indian tech companies — a significantly better email-yield profile than
VC-portfolio or GitHub-org bootstrap sources.

No authentication required. robots.txt checked before every request.
Rate-limited to 1 request per 3 seconds.
"""

import logging
import re
from typing import List

import httpx
from bs4 import BeautifulSoup

from scraper.sources.company_discovery.base import BaseCompanySource
from scraper.sources.company_discovery.enrichment.domain_utils import (
    is_job_board,
    normalize_apex_domain,
)

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 20.0
_NASSCOM_BASE = "https://nasscom.in"
_NASSCOM_DIRECTORY_URL = "https://nasscom.in/member-directory"

# Maximum pages to crawl from directory listing (safety cap)
_MAX_PAGES = 30

# Regex to find a plausible website URL in member profile text
_URL_RE = re.compile(
    r"https?://[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}(?:/[^\s\"'<>]*)?",
    re.IGNORECASE,
)


class NasscomDirectoryCrawler(BaseCompanySource):
    """Crawls the NASSCOM public member directory to collect Indian tech company domains.

    Targets the public listing at nasscom.in/member-directory. Each member
    card typically contains company name, description, and a website link.
    Only the apex domain is extracted — email extraction is handled by the
    enrichment pipeline downstream.

    Returns:
        List of unique normalised apex domain strings.
    """

    def get_source_tag(self) -> str:
        return "directory"

    async def discover(self, **kwargs) -> List[str]:
        """Crawl NASSCOM member directory and return apex domains.

        Returns:
            List of unique normalised apex domain strings.
        """
        domains: List[str] = []

        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "JobHunterBot/1.0 (jobhunter.app)",
                "Accept": "text/html,application/xhtml+xml",
            },
        ) as client:
            # Check robots.txt before crawling
            robots_allowed = await self._check_robots(client, _NASSCOM_BASE)
            if not robots_allowed:
                logger.info(
                    "NASSCOM directory robots.txt blocked crawl",
                    extra={"url": _NASSCOM_DIRECTORY_URL},
                )
                return []

            # Fetch first page to discover pagination
            first_page_domains, total_pages = await self._fetch_directory_page(
                client, _NASSCOM_DIRECTORY_URL, page=1
            )
            domains.extend(first_page_domains)

            # Crawl remaining pages up to cap
            pages_to_fetch = min(total_pages, _MAX_PAGES)
            for page_num in range(2, pages_to_fetch + 1):
                await self.rate_limiter.wait("nasscom")
                page_url = f"{_NASSCOM_DIRECTORY_URL}?page={page_num}"
                page_domains, _ = await self._fetch_directory_page(
                    client, page_url, page=page_num
                )
                if not page_domains:
                    break
                domains.extend(page_domains)

        # Deduplicate
        seen: set = set()
        unique: List[str] = []
        for d in domains:
            if d and d not in seen:
                seen.add(d)
                unique.append(d)

        logger.info(
            "NASSCOM crawl complete",
            extra={"unique_domains": len(unique)},
        )
        return unique

    async def _fetch_directory_page(
        self,
        client: httpx.AsyncClient,
        url: str,
        page: int,
    ) -> tuple[List[str], int]:
        """Fetch one page of the NASSCOM member directory.

        Args:
            client: Shared httpx client.
            url: Full URL to fetch.
            page: Page number (for logging).

        Returns:
            Tuple of (list of apex domains, total_pages detected).
        """
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.debug(
                    "NASSCOM page non-200",
                    extra={"url": url, "status": resp.status_code},
                )
                return [], 1
        except Exception as exc:
            logger.warning(
                "NASSCOM page fetch failed",
                extra={"url": url, "error": str(exc)},
            )
            return [], 1

        soup = BeautifulSoup(resp.text, "lxml")
        domains = self._extract_domains_from_page(soup)
        total_pages = self._detect_total_pages(soup)

        logger.debug(
            "NASSCOM page fetched",
            extra={"page": page, "domains": len(domains), "total_pages": total_pages},
        )
        return domains, total_pages

    def _extract_domains_from_page(self, soup: BeautifulSoup) -> List[str]:
        """Extract company website domains from a parsed directory page.

        Tries multiple strategies in priority order:
        1. Anchor tags with href pointing to external sites
        2. Text content matching URL pattern in member cards

        Args:
            soup: Parsed BeautifulSoup of the page.

        Returns:
            List of normalised apex domain strings.
        """
        domains: List[str] = []

        # Strategy 1: <a href="https://..."> links inside member cards
        # NASSCOM directory cards typically use class names like
        # 'member-card', 'views-row', 'member-item', or similar
        for tag in soup.find_all("a", href=True):
            href: str = tag["href"].strip()
            # Skip internal nasscom.in links and empty hrefs
            if not href or href.startswith("#") or href.startswith("/"):
                continue
            if "nasscom.in" in href:
                continue
            apex = normalize_apex_domain(href)
            if apex and not is_job_board(apex):
                domains.append(apex)

        # Strategy 2: URL patterns in visible text (fallback for JS-rendered links)
        if not domains:
            text = soup.get_text(separator=" ")
            for match in _URL_RE.finditer(text):
                url = match.group(0)
                if "nasscom.in" in url:
                    continue
                apex = normalize_apex_domain(url)
                if apex and not is_job_board(apex):
                    domains.append(apex)

        return domains

    def _detect_total_pages(self, soup: BeautifulSoup) -> int:
        """Detect total page count from pagination elements.

        Falls back to 1 if no pagination is found.

        Args:
            soup: Parsed BeautifulSoup of the page.

        Returns:
            Total number of pages as integer.
        """
        # Try common pagination patterns
        # Pattern 1: <a href="?page=N"> — last numbered link
        max_page = 1
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            match = re.search(r"[?&]page=(\d+)", href)
            if match:
                page_num = int(match.group(1))
                if page_num > max_page:
                    max_page = page_num

        return max_page

    async def _check_robots(
        self, client: httpx.AsyncClient, base_url: str
    ) -> bool:
        """Quick robots.txt check for the NASSCOM directory path.

        Args:
            client: Shared httpx client.
            base_url: Base URL of the site.

        Returns:
            True if crawling is allowed, False otherwise.
        """
        try:
            resp = await client.get(f"{base_url}/robots.txt")
            if resp.status_code != 200:
                # No robots.txt — crawling allowed by default
                return True
            text = resp.text.lower()
            # Check for explicit disallow of /member-directory or catch-all
            lines = [raw.strip() for raw in text.splitlines()]
            in_our_agent = False
            for line in lines:
                if line.startswith("user-agent:"):
                    agent = line.split(":", 1)[1].strip()
                    in_our_agent = agent in ("*", "jobhunterbot")
                if in_our_agent and line.startswith("disallow:"):
                    path = line.split(":", 1)[1].strip()
                    if path in ("/", "/member-directory"):
                        return False
            return True
        except Exception:
            return True
