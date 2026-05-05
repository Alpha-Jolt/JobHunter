"""Generic helper utilities."""

import re
from typing import Optional


def slugify(text: str) -> str:
    """Convert text to lowercase slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def truncate(text: Optional[str], max_len: int = 200) -> Optional[str]:
    """Truncate text to max_len characters."""
    if not text:
        return text
    return text[:max_len] + "…" if len(text) > max_len else text


def safe_int(value, default: Optional[int] = None) -> Optional[int]:
    """Convert value to int, returning default on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
