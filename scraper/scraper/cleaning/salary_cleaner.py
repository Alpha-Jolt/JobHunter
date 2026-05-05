"""Salary string parsing and INR normalisation."""

import re
from typing import Optional, Tuple

_NUM_RE = re.compile(r"[\d,]+(?:\.\d+)?")

CONVERSION_RATES = {
    "USD": 83.0,
    "GBP": 104.0,
    "EUR": 90.0,
    "INR": 1.0,
}

_NON_NUMERIC_PHRASES = ("negotiable", "competitive", "not disclosed", "as per")


class SalaryCleaner:
    """Parse salary strings into (min_inr, max_inr, original_currency)."""

    @staticmethod
    def clean_salary(
        salary_raw: Optional[str],
    ) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Parse salary string.

        Returns:
            (min_inr, max_inr, original_currency) — any element may be None.
        """
        if not salary_raw:
            return None, None, None

        text = salary_raw.lower().strip()

        if any(phrase in text for phrase in _NON_NUMERIC_PHRASES):
            return None, None, None

        currency = SalaryCleaner._detect_currency(salary_raw)
        rate = CONVERSION_RATES.get(currency, 1.0)

        numbers = [float(n.replace(",", "")) for n in _NUM_RE.findall(salary_raw)]
        if not numbers:
            return None, None, None

        # Normalise units (K, Lac/Lakh, L)
        numbers = [SalaryCleaner._normalize_units(n, text) for n in numbers]

        # Detect period — convert monthly to annual
        is_monthly = any(kw in text for kw in ("per month", "/month", "p.m.", "monthly"))
        if is_monthly:
            numbers = [n * 12 for n in numbers]

        salary_min = int(numbers[0] * rate) if len(numbers) >= 1 else None
        salary_max = int(numbers[1] * rate) if len(numbers) >= 2 else None

        # Single number → treat as max
        if salary_max is None and salary_min is not None:
            salary_max = salary_min
            salary_min = None

        return salary_min, salary_max, currency

    @staticmethod
    def _detect_currency(text: str) -> str:
        if "₹" in text or "inr" in text.lower():
            return "INR"
        if "$" in text or "usd" in text.lower():
            return "USD"
        if "£" in text or "gbp" in text.lower():
            return "GBP"
        if "€" in text or "eur" in text.lower():
            return "EUR"
        return "INR"  # Default for Indian job boards

    @staticmethod
    def _normalize_units(value: float, text: str) -> float:
        """Convert K / Lac / Lakh / L to absolute value."""
        if any(kw in text for kw in ("lac", "lakh", " l ", "lpa")):
            return value * 100_000
        if "k" in text:
            return value * 1_000
        return value
