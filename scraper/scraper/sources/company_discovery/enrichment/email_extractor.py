"""Email extractor — crawls contact pages and extracts emails from page content."""

import logging
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from scraper.sources.company_discovery.enrichment.email_classifier import (
    classify_email,
    extract_emails_from_text,
    is_valid_email,
)

logger = logging.getLogger(__name__)

# Pages to crawl within a domain to find contact emails
CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/team",
    "/people",
    "/hr",
]

_HTTP_TIMEOUT = 10.0
_RATE_LIMIT_SECONDS = 3.0


class EmailExtractor:
    """Crawls contact/about pages and extracts classified emails.

    Only extracts emails that are explicitly published in page content.
    Guessed patterns are never stored.

    Args:
        timeout: HTTP request timeout in seconds.
        rate_limit_seconds: Minimum pause between requests to the same domain.
    """

    def __init__(
        self,
        timeout: float = _HTTP_TIMEOUT,
        rate_limit_seconds: float = _RATE_LIMIT_SECONDS,
    ) -> None:
        self._timeout = timeout
        self._rate_limit_seconds = rate_limit_seconds

    async def extract(self, domain: str) -> Dict[str, List[str]]:
        """Crawl contact pages and return classified email lists.

        Args:
            domain: Apex domain string (e.g. ``acme.com``).

        Returns:
            Dict with keys ``career_emails`` and ``contact_emails``,
            each containing a list of unique, format-valid email strings.
        """
        base = f"https://{domain}"
        all_emails: List[str] = []

        async with httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
            headers={"User-Agent": "JobHunterBot/1.0"},
        ) as client:
            # Always crawl homepage header/footer — common email placement
            homepage_emails = await self._extract_from_url(client, base)
            all_emails.extend(homepage_emails)

            # Crawl each contact path
            for path in CONTACT_PATHS:
                url = base + path
                page_emails = await self._extract_from_url(client, url)
                all_emails.extend(page_emails)

        return self._classify_and_deduplicate(all_emails)

    async def _extract_from_url(
        self, client: httpx.AsyncClient, url: str
    ) -> List[str]:
        """Fetch a URL and extract all valid emails from page content.

        Extracts from:
        1. ``mailto:`` link hrefs (highest quality)
        2. Visible page text via regex
        3. Schema.org ContactPoint JSON-LD ``email`` field

        Args:
            client: Shared httpx client for the session.
            url: Full URL to fetch.

        Returns:
            List of format-valid email strings (may contain duplicates).
        """
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return []
            html = resp.text
        except Exception as exc:
            logger.debug(
                "Email extraction fetch failed",
                extra={"url": url, "error": str(exc)},
            )
            return []

        emails: List[str] = []
        soup = BeautifulSoup(html, "lxml")

        # 1. Parse mailto: links
        for tag in soup.find_all("a", href=True):
            href: str = tag["href"]
            if href.startswith("mailto:"):
                raw_email = href[7:].split("?")[0].strip().lower()
                if is_valid_email(raw_email):
                    emails.append(raw_email)

        # 2. Regex extraction from visible text
        text_content = soup.get_text(separator=" ")
        text_emails = extract_emails_from_text(text_content)
        emails.extend(text_emails)

        # 3. Schema.org ContactPoint JSON-LD
        json_ld_emails = _extract_from_json_ld(html)
        emails.extend(json_ld_emails)

        return emails

    def _classify_and_deduplicate(
        self, raw_emails: List[str]
    ) -> Dict[str, List[str]]:
        """Classify emails into career/contact buckets and deduplicate.

        Args:
            raw_emails: Flat list of raw email strings (may contain duplicates).

        Returns:
            Dict with ``career_emails`` and ``contact_emails`` lists.
        """
        career_seen: set = set()
        contact_seen: set = set()
        career_emails: List[str] = []
        contact_emails: List[str] = []

        for email in raw_emails:
            email = email.strip().lower()
            result = classify_email(email)
            if result is None:
                continue
            category, _trust = result
            if category == "career" and email not in career_seen:
                career_seen.add(email)
                career_emails.append(email)
            elif category == "general" and email not in contact_seen:
                contact_seen.add(email)
                contact_emails.append(email)

        return {
            "career_emails": career_emails,
            "contact_emails": contact_emails,
        }


def _extract_from_json_ld(html: str) -> List[str]:
    """Extract emails from Schema.org ContactPoint JSON-LD blocks.

    Args:
        html: Raw HTML string.

    Returns:
        List of email strings found in JSON-LD data.
    """
    import json

    emails: List[str] = []
    soup = BeautifulSoup(html, "lxml")

    for script_tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script_tag.string or "")
        except Exception:
            continue

        # Support both single dict and list of dicts
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            _collect_emails_from_node(node, emails)

    return [e for e in emails if is_valid_email(e)]


def _collect_emails_from_node(node: object, emails: List[str]) -> None:
    """Recursively collect ``email`` values from a JSON-LD node.

    Args:
        node: Parsed JSON object (dict or list).
        emails: List to append found emails to.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key.lower() == "email" and isinstance(value, str):
                emails.append(value.strip().lower())
            else:
                _collect_emails_from_node(value, emails)
    elif isinstance(node, list):
        for item in node:
            _collect_emails_from_node(item, emails)


def get_email_trust(email: str) -> Optional[str]:
    """Return trust level for a single email address.

    Args:
        email: Validated email string.

    Returns:
        ``unverified`` or ``low_trust``, or None if invalid.
    """
    result = classify_email(email)
    if result is None:
        return None
    _category, trust = result
    return trust
