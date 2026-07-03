"""ATS platform detector — inspects career page DOM for known ATS patterns."""

import logging
from typing import Optional

from playwright.async_api import Page

logger = logging.getLogger(__name__)

# Maps ATS platform key → list of domain substrings to match
ATS_PATTERNS: dict[str, list[str]] = {
    "greenhouse": ["boards.greenhouse.io", "greenhouse.io"],
    "lever": ["jobs.lever.co", "lever.co"],
    "ashby": ["jobs.ashby.com", "ashby.com", "ashbyhq.com"],
    "workday": ["workdayjobs.com", "myworkdayjobs.com"],
    "smartrecruiters": ["smartrecruiters.com"],
    "bamboohr": ["bamboohr.com"],
    "teamtailor": ["teamtailor.com"],
    "recruitee": ["recruitee.com"],
    "jazzhr": ["jazzhr.com", "resumatorjobs.com"],
    "workable": ["apply.workable.com", "workable.com"],
}

# CSS selectors / attributes to collect candidate URLs from the page
_CANDIDATE_SELECTORS = [
    "iframe[src]",
    "script[src]",
    "form[action]",
    "a[href]",
]

# Apply button text patterns
_APPLY_TEXT_PATTERNS = ["apply", "apply now", "submit application", "apply here"]


async def detect_ats(page: Page) -> str:
    """Inspect the loaded career page and return the detected ATS platform key.

    Checks iframes, scripts, form actions, and outbound links for known ATS
    domain patterns. Also checks apply button hrefs.

    Args:
        page: Playwright Page already loaded at the career page URL.

    Returns:
        ATS platform key string (e.g. ``greenhouse``), ``custom`` if a career
        page exists but no known ATS is detected, or ``none`` if detection fails.
    """
    candidate_urls: list[str] = []

    try:
        # Collect URLs from all candidate element attributes
        for selector in _CANDIDATE_SELECTORS:
            attr = selector.split("[")[1].rstrip("]")
            elements = await page.query_selector_all(selector)
            for el in elements:
                val = await el.get_attribute(attr)
                if val:
                    candidate_urls.append(val.lower())

        # Also collect apply button hrefs
        for pattern in _APPLY_TEXT_PATTERNS:
            btns = await page.query_selector_all(f'a:has-text("{pattern}")')
            for btn in btns:
                href = await btn.get_attribute("href")
                if href:
                    candidate_urls.append(href.lower())

    except Exception as exc:
        logger.debug("ATS detection DOM query failed", extra={"error": str(exc)})
        return "none"

    # Match collected URLs against known ATS patterns
    for platform, patterns in ATS_PATTERNS.items():
        for url in candidate_urls:
            if any(p in url for p in patterns):
                logger.debug("ATS detected", extra={"platform": platform})
                return platform

    return "custom"


def detect_ats_from_html(html: str) -> str:
    """Inspect raw HTML string for ATS patterns (no Playwright required).

    Used as a fallback when full page render is not available.

    Args:
        html: Raw HTML content of the career page.

    Returns:
        ATS platform key string or ``custom``.
    """
    html_lower = html.lower()
    for platform, patterns in ATS_PATTERNS.items():
        if any(p in html_lower for p in patterns):
            return platform
    return "custom"


def extract_ats_slug(ats_platform: str, career_page_url: str) -> Optional[str]:
    """Extract the company slug from a known ATS career page URL.

    Used by Module 2 to call ATS public APIs without manual configuration.

    Args:
        ats_platform: Detected ATS platform key.
        career_page_url: The company's career page URL.

    Returns:
        Company slug string, or None if not extractable.

    Examples:
        ``https://boards.greenhouse.io/acmecorp`` → ``acmecorp``
        ``https://jobs.lever.co/acme`` → ``acme``
        ``https://jobs.ashby.com/acme-inc`` → ``acme-inc``
    """
    url_lower = career_page_url.lower().rstrip("/")

    slug_patterns = {
        "greenhouse": ["boards.greenhouse.io/", "greenhouse.io/"],
        "lever": ["jobs.lever.co/", "lever.co/jobs/"],
        "ashby": ["jobs.ashby.com/", "ashbyhq.com/"],
    }

    patterns = slug_patterns.get(ats_platform)
    if not patterns:
        return None

    for pattern in patterns:
        idx = url_lower.find(pattern)
        if idx != -1:
            slug = url_lower[idx + len(pattern):].split("/")[0].split("?")[0]
            return slug if slug else None

    return None
