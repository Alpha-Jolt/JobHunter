"""GitHub organization crawler — discovers Indian company domains via GitHub public API."""

import logging
import os
from typing import List, Optional

import httpx

from scraper.sources.company_discovery.base import BaseCompanySource
from scraper.sources.company_discovery.enrichment.domain_utils import (
    is_job_board,
    normalize_apex_domain,
)

logger = logging.getLogger(__name__)

_GITHUB_SEARCH_URL = "https://api.github.com/search/users"
_GITHUB_ORG_URL = "https://api.github.com/orgs/{login}"
_HTTP_TIMEOUT = 15.0
_RATE_LIMIT_KEY = "github_api"
_PER_PAGE = 100
_MAX_PAGES_PER_QUERY = 10  # GitHub limits search to 1,000 results total

# Location-based org search queries
_SEARCH_QUERIES = [
    "location:India type:org language:Python",
    "location:India type:org language:JavaScript",
    "location:India type:org language:Java",
    "location:Bangalore type:org",
    "location:Mumbai type:org",
    "location:Chennai type:org",
    "location:Hyderabad type:org",
    "location:Pune type:org",
    "location:Delhi type:org",
    "location:Coimbatore type:org",
    "location:Ahmedabad type:org",
    "location:Kolkata type:org",
]


class GitHubOrgCrawler(BaseCompanySource):
    """Discovers Indian company domains from GitHub organization profiles.

    Queries the GitHub public search API for organizations located in India,
    then fetches each org's profile to extract the ``blog`` field (company website).

    Rate limits: 60 req/hour unauthenticated; 5,000/hour with GITHUB_TOKEN env var.

    Args:
        github_token: Optional personal access token for higher rate limits.
            If None, falls back to GITHUB_TOKEN env variable.
    """

    def __init__(self, github_token: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._token = github_token or os.environ.get("GITHUB_TOKEN")

    def get_source_tag(self) -> str:
        return "github_org"

    def _headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "JobHunterBot/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def discover(self, **kwargs) -> List[str]:
        """Search GitHub for Indian orgs and extract company website domains.

        Returns:
            List of unique, normalised apex domain strings.
        """
        all_domains: List[str] = []

        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            headers=self._headers(),
        ) as client:
            for query in _SEARCH_QUERIES:
                domains = await self._process_query(client, query)
                logger.info(
                    "GitHub query processed",
                    extra={"query": query, "domains": len(domains)},
                )
                all_domains.extend(domains)
                await self.rate_limiter.wait(_RATE_LIMIT_KEY)

        # Deduplicate
        seen: set = set()
        unique: List[str] = []
        for d in all_domains:
            if d and d not in seen:
                seen.add(d)
                unique.append(d)

        logger.info(
            "GitHub org discovery complete",
            extra={"total_unique_domains": len(unique)},
        )
        return unique

    async def _process_query(
        self, client: httpx.AsyncClient, query: str
    ) -> List[str]:
        """Search for orgs matching a query and collect their website domains.

        Args:
            client: Shared httpx client.
            query: GitHub search query string.

        Returns:
            List of apex domain strings.
        """
        domains: List[str] = []

        for page in range(1, _MAX_PAGES_PER_QUERY + 1):
            logins = await self._search_orgs(client, query, page)
            if not logins:
                break

            for login in logins:
                blog = await self._get_org_blog(client, login)
                if blog:
                    apex = normalize_apex_domain(blog)
                    if apex and not is_job_board(apex):
                        domains.append(apex)
                await self.rate_limiter.wait(_RATE_LIMIT_KEY)

        return domains

    async def _search_orgs(
        self, client: httpx.AsyncClient, query: str, page: int
    ) -> List[str]:
        """Return org login names from a search results page.

        Args:
            client: Shared httpx client.
            query: GitHub search query string.
            page: Page number (1-based).

        Returns:
            List of org login strings.
        """
        try:
            resp = await client.get(
                _GITHUB_SEARCH_URL,
                params={"q": query, "per_page": _PER_PAGE, "page": page},
            )
        except Exception as exc:
            logger.debug(
                "GitHub search request failed",
                extra={"query": query, "error": str(exc)},
            )
            return []

        # Respect rate limits
        remaining = int(resp.headers.get("X-RateLimit-Remaining", "60"))
        if remaining < 5:
            import time
            reset_at = int(resp.headers.get("X-RateLimit-Reset", str(int(time.time()) + 60)))
            sleep_seconds = max(reset_at - int(time.time()), 5)
            logger.info(
                "GitHub rate limit near — pausing",
                extra={"sleep_seconds": sleep_seconds},
            )
            import asyncio
            await asyncio.sleep(sleep_seconds)

        if resp.status_code == 403:
            logger.warning("GitHub API rate limited or forbidden")
            return []

        if resp.status_code != 200:
            logger.debug(
                "GitHub search non-200",
                extra={"status": resp.status_code, "query": query},
            )
            return []

        data = resp.json()
        return [item["login"] for item in data.get("items", []) if item.get("login")]

    async def _get_org_blog(
        self, client: httpx.AsyncClient, login: str
    ) -> Optional[str]:
        """Fetch an org's profile and return the ``blog`` field.

        Args:
            client: Shared httpx client.
            login: GitHub organisation login name.

        Returns:
            Blog URL string, or None if not set or unreachable.
        """
        try:
            resp = await client.get(_GITHUB_ORG_URL.format(login=login))
            if resp.status_code != 200:
                return None
            data = resp.json()
            blog = data.get("blog", "").strip()
            return blog if blog else None
        except Exception as exc:
            logger.debug(
                "GitHub org fetch failed",
                extra={"login": login, "error": str(exc)},
            )
            return None
