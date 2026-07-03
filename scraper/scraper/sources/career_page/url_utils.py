"""URL normalisation and hashing utilities for career page job deduplication."""

import hashlib
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

# Tracking parameters stripped from job URLs before hashing
_TRACKING_PARAMS = frozenset([
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "referrer", "gh_src", "lever-source", "source", "via",
    "fbclid", "gclid", "msclkid", "yclid",
])

# URL path fragments that indicate a job listing page
JOB_PATH_PATTERNS = [
    "/job/", "/jobs/", "/position/", "/positions/",
    "/opening/", "/openings/", "/role/", "/roles/",
    "/vacancy/", "/vacancies/", "/career/", "/careers/",
    "/apply/",
]


def normalize_job_url(url: str) -> str:
    """Normalise a job listing URL for stable deduplication.

    Steps:
    1. Lowercase
    2. Strip tracking query parameters
    3. Strip trailing slash

    Args:
        url: Raw job URL string.

    Returns:
        Normalised URL string.
    """
    url = url.strip().lower()
    try:
        parsed = urlparse(url)
        # Filter out tracking params
        filtered_params = {
            k: v
            for k, v in parse_qs(parsed.query, keep_blank_values=True).items()
            if k not in _TRACKING_PARAMS
        }
        clean = parsed._replace(query=urlencode(filtered_params, doseq=True))
        return urlunparse(clean).rstrip("/")
    except Exception:
        return url.rstrip("/")


def compute_url_hash(normalized_url: str) -> str:
    """Return MD5 hex digest of a normalised job URL.

    Args:
        normalized_url: Output of normalize_job_url().

    Returns:
        32-character MD5 hex string.
    """
    return hashlib.md5(normalized_url.encode("utf-8")).hexdigest()


def compute_content_hash(job_title: str, description: str) -> str:
    """Return MD5 hex digest of normalised title + description.

    Used for change detection — unchanged content produces the same hash.

    Args:
        job_title: Raw or cleaned job title string.
        description: Raw or cleaned job description text.

    Returns:
        32-character MD5 hex string.
    """
    normalized = (
        re.sub(r"\s+", " ", (job_title or "").strip().lower())
        + " "
        + re.sub(r"\s+", " ", (description or "").strip().lower())
    )
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def is_job_url(url: str) -> bool:
    """Return True if the URL path matches a known job listing pattern.

    Args:
        url: URL string to check.

    Returns:
        True if the URL likely points to a job listing page.
    """
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in JOB_PATH_PATTERNS)
