"""Unit tests for robots.txt checker."""

import pytest
import respx
import httpx

from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker


ROBOTS_ALLOW_ALL = "User-agent: *\nAllow: /"
ROBOTS_BLOCK_CAREERS = "User-agent: *\nDisallow: /careers"
ROBOTS_BLOCK_ALL = "User-agent: *\nDisallow: /"
ROBOTS_BLOCK_BOT = "User-agent: JobHunterBot\nDisallow: /"


@pytest.mark.asyncio
class TestRobotsChecker:
    async def test_allows_path_when_robots_permits(self):
        checker = RobotsChecker()
        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(200, text=ROBOTS_ALLOW_ALL)
            )
            allowed = await checker.is_allowed("acme.com", "/careers")
        assert allowed is True

    async def test_blocks_path_when_disallowed(self):
        checker = RobotsChecker()
        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(200, text=ROBOTS_BLOCK_CAREERS)
            )
            allowed = await checker.is_allowed("acme.com", "/careers")
        assert allowed is False

    async def test_allows_other_path_when_only_careers_blocked(self):
        checker = RobotsChecker()
        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(200, text=ROBOTS_BLOCK_CAREERS)
            )
            allowed = await checker.is_allowed("acme.com", "/about")
        assert allowed is True

    async def test_allows_when_robots_txt_missing(self):
        checker = RobotsChecker()
        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(404)
            )
            allowed = await checker.is_allowed("acme.com", "/careers")
        assert allowed is True

    async def test_allows_on_fetch_timeout(self):
        checker = RobotsChecker(timeout=0.001)
        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                side_effect=httpx.TimeoutException("timeout")
            )
            allowed = await checker.is_allowed("acme.com", "/careers")
        assert allowed is True

    async def test_caches_robots_txt(self):
        checker = RobotsChecker()
        call_count = 0

        with respx.mock:
            def handler(request):
                nonlocal call_count
                call_count += 1
                return httpx.Response(200, text=ROBOTS_ALLOW_ALL)

            respx.get("https://acme.com/robots.txt").mock(side_effect=handler)
            await checker.is_allowed("acme.com", "/careers")
            await checker.is_allowed("acme.com", "/contact")

        assert call_count == 1  # fetched only once

    async def test_is_domain_enrichable_blocked_domain(self):
        checker = RobotsChecker()
        with respx.mock:
            respx.get("https://blocked.com/robots.txt").mock(
                return_value=httpx.Response(200, text=ROBOTS_BLOCK_ALL)
            )
            result = await checker.is_domain_enrichable("blocked.com")
        assert result is False

    async def test_clear_cache(self):
        checker = RobotsChecker()
        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(200, text=ROBOTS_ALLOW_ALL)
            )
            await checker.is_allowed("acme.com", "/careers")
        assert "acme.com" in checker._cache
        checker.clear_cache()
        assert "acme.com" not in checker._cache
