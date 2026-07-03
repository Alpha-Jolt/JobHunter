"""Company metadata extractor — extracts name, industry, location from page meta/structured data."""

import json
import logging
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 10.0


class MetadataExtractor:
    """Extracts company metadata from a domain's homepage.

    Sources checked in priority order:
    1. Schema.org Organization JSON-LD
    2. Open Graph meta tags (og:site_name, og:title)
    3. HTML <title> tag fallback

    All metadata is advisory — higher-confidence data is never overwritten.

    Args:
        timeout: HTTP request timeout in seconds.
    """

    def __init__(self, timeout: float = _HTTP_TIMEOUT) -> None:
        self._timeout = timeout

    async def extract(self, domain: str) -> dict:
        """Fetch the homepage and extract available company metadata.

        Args:
            domain: Apex domain string (e.g. ``acme.com``).

        Returns:
            Dict with optional keys: ``company_name``, ``industry``,
            ``hq_location``, ``logo_url``.
        """
        base = f"https://{domain}"
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": "JobHunterBot/1.0"},
            ) as client:
                resp = await client.get(base)
                if resp.status_code != 200:
                    return {}
                html = resp.text
        except Exception as exc:
            logger.debug(
                "Metadata fetch failed",
                extra={"domain": domain, "error": str(exc)},
            )
            return {}

        return _parse_metadata(html)


def _parse_metadata(html: str) -> dict:
    """Parse metadata from an HTML page.

    Args:
        html: Raw HTML string.

    Returns:
        Dict of extracted metadata fields (only non-None values included).
    """
    soup = BeautifulSoup(html, "lxml")
    result: dict = {}

    # --- 1. Schema.org Organization JSON-LD ---
    org_data = _extract_org_json_ld(soup)
    if org_data:
        if org_data.get("name"):
            result["company_name"] = _clean_text(org_data["name"])
        if org_data.get("industry") or org_data.get("knowsAbout"):
            result["industry"] = _clean_text(
                org_data.get("industry") or org_data.get("knowsAbout", "")
            )
        if org_data.get("address"):
            result["hq_location"] = _extract_location(org_data["address"])
        if org_data.get("logo"):
            logo = org_data["logo"]
            if isinstance(logo, str):
                result["logo_url"] = logo
            elif isinstance(logo, dict) and logo.get("url"):
                result["logo_url"] = logo["url"]

    # --- 2. Open Graph meta tags ---
    og_site_name = _get_meta(soup, property="og:site_name")
    og_image = _get_meta(soup, property="og:image")

    if not result.get("company_name") and og_site_name:
        result["company_name"] = _clean_text(og_site_name)
    if not result.get("logo_url") and og_image:
        result["logo_url"] = og_image

    # --- 3. <title> tag fallback ---
    if not result.get("company_name"):
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            result["company_name"] = _clean_text(title_tag.string.split("|")[0].split("-")[0])

    return {k: v for k, v in result.items() if v}


def _extract_org_json_ld(soup: BeautifulSoup) -> Optional[dict]:
    """Find the first Schema.org Organization node in JSON-LD blocks.

    Args:
        soup: Parsed BeautifulSoup object.

    Returns:
        Organization dict if found, None otherwise.
    """
    for script_tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script_tag.string or "")
        except Exception:
            continue

        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_type = node.get("@type", "")
            if isinstance(node_type, list):
                types = [t.lower() for t in node_type]
            else:
                types = [str(node_type).lower()]
            if "organization" in types or "corporation" in types:
                return node

    return None


def _get_meta(soup: BeautifulSoup, **kwargs) -> Optional[str]:
    """Return the content of a <meta> tag matching the given attributes.

    Args:
        soup: Parsed BeautifulSoup object.
        **kwargs: Attribute key/value pairs to match on the <meta> tag.

    Returns:
        Content string if found, None otherwise.
    """
    tag = soup.find("meta", attrs=kwargs)
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def _extract_location(address: object) -> Optional[str]:
    """Extract a readable location string from a Schema.org address object.

    Args:
        address: Schema.org PostalAddress dict or raw string.

    Returns:
        Location string, or None if not extractable.
    """
    if isinstance(address, str):
        return _clean_text(address) or None

    if not isinstance(address, dict):
        return None

    parts = []
    for field in ("addressLocality", "addressRegion", "addressCountry"):
        val = address.get(field)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
        elif isinstance(val, dict) and val.get("name"):
            parts.append(val["name"].strip())

    return ", ".join(parts) if parts else None


def _clean_text(text: str) -> str:
    """Strip and collapse whitespace in a metadata string.

    Args:
        text: Raw metadata string.

    Returns:
        Cleaned, stripped string.
    """
    return re.sub(r"\s+", " ", text.strip())
