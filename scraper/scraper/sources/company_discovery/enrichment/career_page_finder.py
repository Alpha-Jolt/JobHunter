"""Career page discovery — finds the career section URL for a given domain."""

import logging
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Ordered path patterns to probe (fastest/most common first)
CAREER_PATHS = [
    "/careers", "/jobs", "/career", "/join-us", "/work-with-us",
    "/opportunities", "/hiring", "/vacancies", "/talent", "/openings",
    "/join", "/work-here", "/positions", "/open-roles",
]

# Anchor text patterns for homepage link search (lowercase)
CAREER_LINK_TEXT = [
    "careers", "jobs", "join us", "we're hiring", "we are hiring",
    "open positions", "work with us", "job openings", "join the team",
    "opportunities",
]

_HTTP_TIMEOUT = 10.0


async def find_career_page(domain: str) -> Optional[str]:
    """Find the career page URL for a domain using a three-phase strategy.

    Phase 1 — URL pattern probing (fast, no JS)
    Phase 2 — Homepage link text parsing (handles custom paths)
    Phase 3 — Sitemap parsing (handles obscure career sections)

    Args:
        domain: Apex domain string (e.g. ``acme.com``).

    Returns:
        Full career page URL string if found, None otherwise.
    """
    base = f"https://{domain}"

    # Phase 1 — probe known career URL patterns
    result = await _probe_career_paths(base)
    if result:
        return result

    # Phase 2 — parse homepage links
    result = await _parse_homepage_links(base)
    if result:
        return result

    # Phase 3 — parse sitemap
    result = await _parse_sitemap(base)
    return result


async def _probe_career_paths(base_url: str) -> Optional[str]:
    """Try each career path pattern and return the first that returns HTTP 200.

    Args:
        base_url: Base URL with scheme (e.g. ``https://acme.com``).

    Returns:
        Full URL string if a career page is found, None otherwise.
    """
    async with httpx.AsyncClient(
        timeout=_HTTP_TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": "JobHunterBot/1.0"},
    ) as client:
        for path in CAREER_PATHS:
            url = base_url + path
            try:
                resp = await client.head(url)
                if resp.status_code == 200:
                    logger.debug("Career page found via probe", extra={"url": url})
                    return str(resp.url)
                # Some servers reject HEAD — fall back to GET for a short check
                if resp.status_code in (405, 403):
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        return str(resp.url)
            except Exception:
                continue
    return None


async def _parse_homepage_links(base_url: str) -> Optional[str]:
    """Fetch the homepage and look for career-related anchor links.

    Args:
        base_url: Base URL with scheme.

    Returns:
        Full URL string if a career link is found, None otherwise.
    """
    try:
        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "JobHunterBot/1.0"},
        ) as client:
            resp = await client.get(base_url)
            if resp.status_code != 200:
                return None
            html = resp.text
    except Exception:
        return None

    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        text = (anchor.get_text() or "").strip().lower()
        href = anchor["href"]
        if any(pattern in text for pattern in CAREER_LINK_TEXT):
            return _resolve_url(base_url, href)

    return None


async def _parse_sitemap(base_url: str) -> Optional[str]:
    """Fetch and parse sitemap.xml for career-related URLs.

    Args:
        base_url: Base URL with scheme.

    Returns:
        Career URL if found in sitemap, None otherwise.
    """
    career_keywords = ["/career", "/jobs", "/position", "/opening", "/role", "/vacancy"]
    sitemap_url = base_url + "/sitemap.xml"

    try:
        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "JobHunterBot/1.0"},
        ) as client:
            resp = await client.get(sitemap_url)
            if resp.status_code != 200:
                return None
            xml = resp.text
    except Exception:
        return None

    soup = BeautifulSoup(xml, "lxml-xml")

    # Handle sitemap index — look for child sitemaps named after careers/jobs
    for sitemap_tag in soup.find_all("sitemap"):
        loc = sitemap_tag.find("loc")
        if loc and any(kw in loc.text.lower() for kw in ["career", "job"]):
            try:
                async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
                    child_resp = await client.get(loc.text.strip())
                    if child_resp.status_code == 200:
                        child_soup = BeautifulSoup(child_resp.text, "lxml-xml")
                        first_loc = child_soup.find("loc")
                        if first_loc:
                            return first_loc.text.strip()
            except Exception:
                continue

    # Scan all <loc> entries in the root sitemap
    for loc in soup.find_all("loc"):
        url = loc.text.strip().lower()
        if any(kw in url for kw in career_keywords):
            return loc.text.strip()

    return None


def _resolve_url(base_url: str, href: str) -> str:
    """Resolve a potentially relative href against the base URL.

    Args:
        base_url: Base URL with scheme (e.g. ``https://acme.com``).
        href: Raw href value from an anchor tag.

    Returns:
        Fully qualified URL string.
    """
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base_url.rstrip("/") + href
    return base_url.rstrip("/") + "/" + href
