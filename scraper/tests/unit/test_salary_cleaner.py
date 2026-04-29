"""Unit tests for SalaryCleaner."""

import pytest

from scraper.cleaning.salary_cleaner import SalaryCleaner


def test_lpa_range():
    mn, mx, cur = SalaryCleaner.clean_salary("5 LPA - 8 LPA")
    assert mn == 500_000
    assert mx == 800_000
    assert cur == "INR"


def test_lac_range():
    mn, mx, cur = SalaryCleaner.clean_salary("₹5 Lac - 8 Lac p.a.")
    assert mn == 500_000
    assert mx == 800_000
    assert cur == "INR"


def test_usd_range():
    mn, mx, cur = SalaryCleaner.clean_salary("$50,000 - $80,000 per year")
    assert cur == "USD"
    assert mn is not None and mx is not None
    assert mn < mx


def test_monthly_to_annual():
    mn, mx, cur = SalaryCleaner.clean_salary("50K - 80K per month")
    assert mn == 600_000
    assert mx == 960_000


def test_negotiable_returns_none():
    mn, mx, cur = SalaryCleaner.clean_salary("Negotiable")
    assert mn is None and mx is None and cur is None


def test_none_input():
    mn, mx, cur = SalaryCleaner.clean_salary(None)
    assert mn is None and mx is None and cur is None


def test_single_number_treated_as_max():
    mn, mx, cur = SalaryCleaner.clean_salary("10 LPA")
    assert mn is None
    assert mx == 1_000_000
