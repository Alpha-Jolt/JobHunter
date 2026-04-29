"""Unit tests for DateCleaner."""

from datetime import datetime, timedelta

import pytest

from scraper.cleaning.date_cleaner import DateCleaner


def test_just_now():
    result = DateCleaner.parse_posted_date("just now")
    assert result is not None
    assert (datetime.utcnow() - result).total_seconds() < 5


def test_days_ago():
    result = DateCleaner.parse_posted_date("3 days ago")
    expected = datetime.utcnow() - timedelta(days=3)
    assert abs((result - expected).total_seconds()) < 10


def test_weeks_ago():
    result = DateCleaner.parse_posted_date("2 weeks ago")
    expected = datetime.utcnow() - timedelta(weeks=2)
    assert abs((result - expected).total_seconds()) < 10


def test_absolute_date_slash():
    result = DateCleaner.parse_posted_date("20/04/2026")
    assert result == datetime(2026, 4, 20)


def test_absolute_date_iso():
    result = DateCleaner.parse_posted_date("2026-04-20")
    assert result == datetime(2026, 4, 20)


def test_absolute_date_long():
    result = DateCleaner.parse_posted_date("April 20, 2026")
    assert result == datetime(2026, 4, 20)


def test_none_input():
    assert DateCleaner.parse_posted_date(None) is None


def test_unparseable_returns_none():
    assert DateCleaner.parse_posted_date("some random text") is None
