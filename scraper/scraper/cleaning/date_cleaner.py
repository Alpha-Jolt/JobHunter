"""Date string parsing to datetime objects."""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional

_RELATIVE_RE = re.compile(
    r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago",
    re.IGNORECASE,
)

_ABSOLUTE_FORMATS = [
    "%B %d, %Y",  # April 20, 2026
    "%b %d, %Y",  # Apr 20, 2026
    "%d %B %Y",  # 20 April 2026
    "%d %b %Y",  # 20 Apr 2026
    "%d/%m/%Y",  # 20/04/2026
    "%Y-%m-%d",  # 2026-04-20
    "%d-%m-%Y",  # 20-04-2026
]

_UNIT_DELTAS = {
    "second": "seconds",
    "minute": "minutes",
    "hour": "hours",
    "day": "days",
    "week": "weeks",
    "month": "days",  # approximate
    "year": "days",  # approximate
}

_UNIT_MULTIPLIERS = {
    "month": 30,
    "year": 365,
}


class DateCleaner:
    """Parse various date string formats into datetime objects."""

    @staticmethod
    def parse_posted_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        text = date_str.strip().lower()
        if text in ("just now", "today", "moments ago"):
            return datetime.now(timezone.utc)
        result = DateCleaner._parse_relative_date(text)
        if result:
            return result
        return DateCleaner._parse_absolute_date(date_str.strip())

    @staticmethod
    def _parse_relative_date(text: str) -> Optional[datetime]:
        match = _RELATIVE_RE.search(text)
        if not match:
            return None
        amount = int(match.group(1))
        unit = match.group(2).lower()
        multiplier = _UNIT_MULTIPLIERS.get(unit, 1)
        delta_key = _UNIT_DELTAS.get(unit, "days")
        return datetime.now(timezone.utc) - timedelta(**{delta_key: amount * multiplier})

    @staticmethod
    def _parse_absolute_date(text: str) -> Optional[datetime]:
        for fmt in _ABSOLUTE_FORMATS:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None
