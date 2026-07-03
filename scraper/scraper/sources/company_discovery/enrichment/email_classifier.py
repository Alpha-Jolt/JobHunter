"""Deterministic email classifier — no AI, keyword matching only."""

import re
from typing import Optional, Tuple

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

HR_EMAIL_KEYWORDS = frozenset([
    "careers", "career", "jobs", "job", "recruitment", "recruit",
    "talent", "hiring", "hr", "people", "join", "apply", "applications",
    "staffing", "resumes", "cv", "work",
])

FREE_WEBMAIL_DOMAINS = frozenset([
    "gmail.com", "yahoo.com", "yahoo.co.in", "hotmail.com", "rediffmail.com",
    "outlook.com", "ymail.com", "live.com", "aol.com", "protonmail.com",
])


def is_valid_email(email: str) -> bool:
    """Return True if email matches a valid format.

    Args:
        email: Raw email string.

    Returns:
        True if format-valid, False otherwise.
    """
    return bool(_EMAIL_RE.match(email.strip()))


def classify_email(email: str) -> Optional[Tuple[str, str]]:
    """Classify an email as career or general, and assess trust level.

    Guessed patterns are never accepted — only call this with emails
    extracted from actual page content.

    Args:
        email: Raw email string.

    Returns:
        Tuple of (category, trust_level) where:
            category: ``career`` | ``general``
            trust_level: ``unverified`` | ``low_trust``
        Returns None if the email fails format validation.
    """
    email = email.strip().lower()

    if not is_valid_email(email):
        return None

    parts = email.split("@", 1)
    if len(parts) != 2:
        return None

    local_part, domain = parts[0], parts[1]

    trust = "low_trust" if domain in FREE_WEBMAIL_DOMAINS else "unverified"
    category = "career" if any(kw in local_part for kw in HR_EMAIL_KEYWORDS) else "general"

    return category, trust


def extract_emails_from_text(text: str) -> list:
    """Extract all format-valid email addresses from a text block.

    Args:
        text: Raw page text or HTML-stripped content.

    Returns:
        List of unique, format-valid, lowercase email strings.
    """
    raw_matches = re.findall(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
        text,
    )
    seen = set()
    result = []
    for m in raw_matches:
        m_lower = m.lower().strip()
        if m_lower not in seen and is_valid_email(m_lower):
            seen.add(m_lower)
            result.append(m_lower)
    return result
