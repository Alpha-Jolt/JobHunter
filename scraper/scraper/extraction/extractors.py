"""Common regex-based field extractors."""

import re
from typing import List

# Compiled patterns — never re-compiled per call
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+91[\-\s]?)?(?:0)?[6-9]\d{9}"  # Indian mobile
    r"|(?:\+\d{1,3}[\-\s]?)?\(?\d{2,4}\)?[\-\s]?\d{3,4}[\-\s]?\d{4}"  # Generic
)
_SALARY_NUM_RE = re.compile(r"[\d,]+(?:\.\d+)?")
_URL_RE = re.compile(r"https?://[^\s\"'<>]+")
_DATE_RE = re.compile(
    r"\b(?:\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
    r"|\d{4}[\/\-]\d{2}[\/\-]\d{2}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)


class JobExtractor:
    """Regex-based field extractors shared across scrapers."""

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        return _EMAIL_RE.findall(text)

    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        return _PHONE_RE.findall(text)

    @staticmethod
    def extract_salary_numbers(text: str) -> List[float]:
        raw = _SALARY_NUM_RE.findall(text)
        result = []
        for r in raw:
            try:
                result.append(float(r.replace(",", "")))
            except ValueError:
                pass
        return result

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        return _URL_RE.findall(text)

    @staticmethod
    def extract_dates(text: str) -> List[str]:
        return _DATE_RE.findall(text)
