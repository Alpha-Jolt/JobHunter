"""Hash generation helpers for deduplication fingerprinting."""

import hashlib


def content_fingerprint(title: str, company: str, location: str) -> str:
    """SHA-256 of normalised title+company+location (first 16 hex chars)."""
    raw = f"{title}|{company}|{location}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def url_fingerprint(url: str) -> str:
    """SHA-256 of URL (first 16 hex chars)."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]
