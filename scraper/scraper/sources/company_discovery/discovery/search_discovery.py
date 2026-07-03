"""DuckDuckGo keyword-driven search discovery for company domains."""

import logging
from typing import List, Optional
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from scraper.sources.company_discovery.base import BaseCompanySource
from scraper.sources.company_discovery.enrichment.domain_utils import (
    is_job_board,
    normalize_apex_domain,
)

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 20.0
_RATE_LIMIT_KEY_DDG = "duckduckgo"
_RATE_LIMIT_KEY_BING = "bing"

# DuckDuckGo HTML endpoint (no Playwright needed — static HTML)
_DDG_URL = "https://html.duckduckgo.com/html/?q={query}"

# Bing HTML fallback
_BING_URL = "https://www.bing.com/search?q={query}"

# Max queries per session before a 5-minute pause
_MAX_QUERIES_PER_SESSION = 15

_CAPTCHA_SIGNALS = ["robot", "captcha", "unusual traffic", "are you a human"]


def build_search_queries(
    role: str,
    location: str,
    experience: str = "fresher",
) -> List[str]:
    """Build keyword query variants from admin input fields.

    Args:
        role: Free-text role keyword (e.g. "full stack developer").
        location: Target location (e.g. "Coimbatore").
        experience: One of "fresher", "intermediate", "advanced".

    Returns:
        List of search query strings.
    """
    queries = [
        f'"{role}" "{location}" jobs hiring',
        f'"{role}" careers India site:.in',
        f'"{role}" "we are hiring" "{location}"',
        f'"{role}" "apply now" India',
    ]
    if experience.lower() == "fresher":
        queries.append(f'"{role}" internship India')
    return queries


class SearchDiscovery(BaseCompanySource):
    """Admin-initiated keyword-driven company discovery via search engines.

    Uses DuckDuckGo HTML endpoint as primary (no API key needed).
    Falls back to Bing HTML if DuckDuckGo blocks or returns CAPTCHA.

    Rate limits:
    - Minimum 3 seconds between queries (enforced by RateLimiter).
    - Maximum 15 queries per session, then 5-minute pause.

    Args:
        max_queries_per_session: Override the session query cap.
    """

    def __init__(
        self,
        max_queries_per_session: int = _MAX_QUERIES_PER_SESSION,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._max_queries_per_session = max_queries_per_session
        self._query_count = 0
        self._captcha_detected = False

    def get_source_tag(self) -> str:
        return "search_discovery"

    async def discover(
        self,
        role: str,
        location: str,
        experience: str = "fresher",
        salary: Optional[str] = None,
        **kwargs,
    ) -> List[str]:
        """Run keyword-driven search discovery and return discovered domains.

        Args:
            role: Free-text role keyword.
            location: Target location.
            experience: "fresher", "intermediate", or "advanced".
            salary: Optional salary range string (not used in queries yet).

        Returns:
            List of unique, normalised apex domain strings.
        """
        queries = build_search_queries(role, location, experience)
        all_domains: List[str] = []

        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; JobHunterBot/1.0)",
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as client:
            for query in queries:
                if self._query_count >= self._max_queries_per_session:
                    logger.info(
                        "Session query cap reached — pausing 5 minutes",
                        extra={"cap": self._max_queries_per_session},
                    )
                    import asyncio
                    await asyncio.sleep(300)
                    self._query_count = 0
                    self._captcha_detected = False

                domains = await self._search(client, query)
                all_domains.extend(domains)
                self._query_count += 1

                rate_key = _RATE_LIMIT_KEY_BING if self._captcha_detected else _RATE_LIMIT_KEY_DDG
                await self.rate_limiter.wait(rate_key)

        seen: set = set()
        unique: List[str] = []
        for d in all_domains:
            if d and d not in seen:
                seen.add(d)
                unique.append(d)

        logger.info(
            "Search discovery complete",
            extra={
                "role": role,
                "location": location,
                "domains": len(unique),
                "queries_run": self._query_count,
            },
        )
        return unique

    async def _search(
        self, client: httpx.AsyncClient, query: str
    ) -> List[str]:
        """Execute a single search query and return extracted domains.

        Tries DuckDuckGo first; falls back to Bing on CAPTCHA detection.

        Args:
            client: Shared httpx client.
            query: Search query string.

        Returns:
            List of apex domain strings from search results.
        """
        if not self._captcha_detected:
            result = await self._search_duckduckgo(client, query)
            if result is not None:
                return result
            # CAPTCHA detected — switch to Bing for this session
            self._captcha_detected = True
            logger.info("DuckDuckGo CAPTCHA detected — switching to Bing fallback")

        return await self._search_bing(client, query)

    async def _search_duckduckgo(
        self, client: httpx.AsyncClient, query: str
    ) -> Optional[List[str]]:
        """Query DuckDuckGo HTML endpoint.

        Args:
            client: Shared httpx client.
            query: Search query string.

        Returns:
            List of apex domains, or None if CAPTCHA/block detected.
        """
        url = _DDG_URL.format(query=quote_plus(query))
        try:
            resp = await client.get(url)
        except Exception as exc:
            logger.debug(
                "DuckDuckGo request failed",
                extra={"query": query, "error": str(exc)},
            )
            return []

        body = resp.text.lower()
        if resp.status_code == 202 or any(s in body for s in _CAPTCHA_SIGNALS):
            return None  # signal CAPTCHA to caller

        return self._parse_ddg_results(resp.text)

    async def _search_bing(
        self, client: httpx.AsyncClient, query: str
    ) -> List[str]:
        """Query Bing HTML endpoint as fallback.

        Args:
            client: Shared httpx client.
            query: Search query string.

        Returns:
            List of apex domain strings.
        """
        url = _BING_URL.format(query=quote_plus(query))
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return []
        except Exception as exc:
            logger.debug(
                "Bing request failed",
                extra={"query": query, "error": str(exc)},
            )
            return []

        return self._parse_bing_results(resp.text)

    def _parse_ddg_results(self, html: str) -> List[str]:
        """Extract result URLs from DuckDuckGo HTML response.

        Args:
            html: Raw HTML string from DDG HTML endpoint.

        Returns:
            List of apex domain strings.
        """
        soup = BeautifulSoup(html, "lxml")
        domains: List[str] = []

        # DuckDuckGo HTML result URLs appear in .result__url elements
        for el in soup.select(".result__url"):
            raw_url = el.get_text(strip=True)
            apex = normalize_apex_domain(raw_url)
            if apex and not is_job_board(apex):
                domains.append(apex)

        # Also check regular result links
        for el in soup.select("a.result__a[href]"):
            apex = normalize_apex_domain(el["href"])
            if apex and not is_job_board(apex):
                domains.append(apex)

        return domains

    def _parse_bing_results(self, html: str) -> List[str]:
        """Extract result URLs from Bing HTML response.

        Args:
            html: Raw HTML string from Bing.

        Returns:
            List of apex domain strings.
        """
        soup = BeautifulSoup(html, "lxml")
        domains: List[str] = []

        # Bing result links are in <h2><a href="..."> inside .b_algo
        for el in soup.select(".b_algo h2 a[href]"):
            apex = normalize_apex_domain(el["href"])
            if apex and not is_job_board(apex):
                domains.append(apex)

        return domains
