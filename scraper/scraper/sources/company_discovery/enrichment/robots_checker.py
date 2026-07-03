"""robots.txt compliance checker — mandatory before any domain request."""

import logging
from typing import Dict
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger(__name__)

_ROBOTS_TIMEOUT = 5.0
_BOT_USER_AGENT = "JobHunterBot"

# Paths checked during enrichment
ENRICHMENT_PATHS = ["/", "/careers", "/jobs", "/contact", "/about"]


class RobotsChecker:
    """Fetches and caches robots.txt per domain for the current session.

    Non-negotiable: enrichment never proceeds if robots.txt blocks the path.

    Args:
        user_agent: User-agent string to check rules against.
        timeout: HTTP timeout in seconds for fetching robots.txt.
    """

    def __init__(
        self,
        user_agent: str = _BOT_USER_AGENT,
        timeout: float = _ROBOTS_TIMEOUT,
    ) -> None:
        self._user_agent = user_agent
        self._timeout = timeout
        self._cache: Dict[str, RobotFileParser] = {}

    async def is_allowed(self, domain: str, path: str) -> bool:
        """Return True if the given path is allowed for the configured user-agent.

        Fetches and caches robots.txt on first call per domain.
        If robots.txt is absent or unreachable, allows access with a warning.

        Args:
            domain: Apex domain string (e.g. ``acme.com``).
            path: URL path to check (e.g. ``/careers``).

        Returns:
            True if access is permitted, False if explicitly disallowed.
        """
        parser = await self._get_parser(domain)
        if parser is None:
            return True  # absent robots.txt → allow, proceed conservatively
        allowed = parser.can_fetch(self._user_agent, path)
        if not allowed:
            logger.info(
                "robots.txt blocked",
                extra={"domain": domain, "path": path, "user_agent": self._user_agent},
            )
        return allowed

    async def is_domain_enrichable(self, domain: str) -> bool:
        """Check all enrichment paths at once. Returns False if any are blocked.

        Args:
            domain: Apex domain string.

        Returns:
            True if all enrichment paths are allowed.
        """
        for path in ENRICHMENT_PATHS:
            if not await self.is_allowed(domain, path):
                return False
        return True

    async def _get_parser(self, domain: str) -> RobotFileParser | None:
        """Return a cached RobotFileParser for the domain, fetching if needed.

        Args:
            domain: Apex domain string.

        Returns:
            RobotFileParser instance, or None if robots.txt could not be fetched.
        """
        if domain in self._cache:
            return self._cache[domain]

        robots_url = f"https://{domain}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                resp = await client.get(robots_url)
            if resp.status_code == 200:
                parser.parse(resp.text.splitlines())
            elif resp.status_code == 404:
                # No robots.txt — allow all
                self._cache[domain] = None
                return None
            else:
                logger.debug(
                    "robots.txt fetch returned non-200",
                    extra={"domain": domain, "status": resp.status_code},
                )
                self._cache[domain] = None
                return None
        except Exception as exc:
            logger.debug(
                "robots.txt fetch failed — proceeding conservatively",
                extra={"domain": domain, "error": str(exc)},
            )
            self._cache[domain] = None
            return None

        self._cache[domain] = parser
        return parser

    def clear_cache(self) -> None:
        """Clear the in-memory robots.txt cache."""
        self._cache.clear()
