"""Field-level validators for canonical job data."""

import re
from typing import Optional

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_URL_RE = re.compile(r"^https?://[^\s]+$")


def is_valid_email(value: Optional[str]) -> bool:
    return bool(value and _EMAIL_RE.match(value))


def is_valid_url(value: Optional[str]) -> bool:
    return bool(value and _URL_RE.match(value))


def clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))
