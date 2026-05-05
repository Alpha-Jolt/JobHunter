"""Date parsing utilities."""

from __future__ import annotations

from datetime import datetime


_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
]


def parse_datetime(value: str | None) -> datetime | None:
    """Parse a datetime string using common formats.

    Args:
        value: Date/datetime string or None.

    Returns:
        datetime object or None if parsing fails.
    """
    if not value:
        return None
    for fmt in _FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None
