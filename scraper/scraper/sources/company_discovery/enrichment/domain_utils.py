"""Domain and company name normalisation utilities for deduplication."""

import hashlib
import re
from typing import Optional
from urllib.parse import urlparse

try:
    import tldextract
    _HAS_TLDEXTRACT = True
except ImportError:
    _HAS_TLDEXTRACT = False

# Known job board / aggregator domains — excluded from company discovery
JOB_BOARD_DOMAINS = frozenset([
    "naukri.com", "linkedin.com", "indeed.com", "shine.com", "glassdoor.com",
    "monster.com", "instahyre.com", "freshersworld.com", "internshala.com",
    "hirist.com", "iimjobs.com", "foundit.in", "timesjobs.com", "angel.co",
    "wellfound.com", "twitter.com", "facebook.com", "instagram.com",
    "youtube.com", "crunchbase.com", "wikipedia.org", "github.com",
    "gitlab.com", "stackoverflow.com", "medium.com", "substack.com",
])

_LEGAL_SUFFIX_RE = re.compile(
    r"\b(pvt\.?\s*ltd\.?|private\s+limited|inc\.?|ltd\.?|llc|llp|corp\.?|"
    r"corporation|limited|technologies|technology|tech|solutions|solution|"
    r"systems|system|software|services|service|consulting|consultancy|"
    r"group|india|global)\b",
    re.IGNORECASE,
)


def normalize_apex_domain(url_or_domain: str) -> Optional[str]:
    """Strip protocol, www., path, port and return lowercase apex domain.

    Uses tldextract when available for accurate TLD handling
    (e.g. ``careers.acme.co.in`` → ``acme.co.in``).
    Falls back to simple netloc extraction when tldextract is absent.

    Args:
        url_or_domain: Raw URL or domain string.

    Returns:
        Normalised apex domain string, or None if the input is invalid.
    """
    if not url_or_domain or not isinstance(url_or_domain, str):
        return None

    raw = url_or_domain.strip().lower()

    # Add scheme so urlparse can handle bare domains
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    try:
        parsed = urlparse(raw)
        netloc = parsed.netloc.split(":")[0]  # strip port
    except Exception:
        return None

    if not netloc:
        return None

    if _HAS_TLDEXTRACT:
        extracted = tldextract.extract(netloc)
        if not extracted.domain or not extracted.suffix:
            return None
        return f"{extracted.domain}.{extracted.suffix}"

    # Fallback: strip www. prefix
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc if "." in netloc else None


def is_job_board(apex_domain: str) -> bool:
    """Return True if the domain is a known job board / aggregator.

    Args:
        apex_domain: Normalised apex domain string.

    Returns:
        True if the domain should be excluded from company discovery.
    """
    return apex_domain in JOB_BOARD_DOMAINS


def normalize_company_name(name: str) -> str:
    """Lowercase, strip legal suffixes, remove non-alphanumeric characters.

    Args:
        name: Raw company name string.

    Returns:
        Normalised name suitable for deduplication fingerprint.
    """
    lowered = name.lower()
    stripped = _LEGAL_SUFFIX_RE.sub("", lowered)
    return re.sub(r"[^a-z0-9]", "", stripped)


def build_dedup_fingerprint(normalized_name: str, apex_domain: str) -> str:
    """Build MD5-based deduplication fingerprint.

    Args:
        normalized_name: Output of normalize_company_name().
        apex_domain: Canonical apex domain string.

    Returns:
        32-character MD5 hex digest.
    """
    raw = (normalized_name + apex_domain).encode("utf-8")
    return hashlib.md5(raw).hexdigest()
