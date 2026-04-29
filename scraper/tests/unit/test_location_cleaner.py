"""Unit tests for LocationCleaner."""

import pytest

from scraper.cleaning.location_cleaner import LocationCleaner


def test_full_location_string():
    city, state = LocationCleaner.clean_location("Bangalore, Karnataka, India")
    assert city == "Bangalore"
    assert state == "Karnataka"


def test_city_only_known():
    city, state = LocationCleaner.clean_location("Bangalore")
    assert city == "Bangalore"
    assert state == "Karnataka"


def test_mumbai_lookup():
    city, state = LocationCleaner.clean_location("Mumbai")
    assert state == "Maharashtra"


def test_none_input():
    city, state = LocationCleaner.clean_location(None)
    assert city is None and state is None


def test_remote_stripped():
    city, state = LocationCleaner.clean_location("Remote, Bangalore")
    assert city == "Bangalore"


def test_unknown_city():
    city, state = LocationCleaner.clean_location("Atlantis")
    assert city == "Atlantis"
    assert state is None
