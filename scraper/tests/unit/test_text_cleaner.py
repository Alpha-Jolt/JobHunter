"""Unit tests for TextCleaner."""

import pytest

from scraper.cleaning.text_cleaner import TextCleaner


def test_clean_text_removes_html_tags():
    assert TextCleaner.clean_text("<b>Hello</b> World") == "Hello World"


def test_clean_text_decodes_entities():
    assert TextCleaner.clean_text("AT&amp;T") == "AT&T"


def test_clean_text_collapses_whitespace():
    assert TextCleaner.clean_text("hello   world") == "hello world"


def test_clean_text_none_returns_none():
    assert TextCleaner.clean_text(None) is None


def test_clean_text_empty_returns_none():
    assert TextCleaner.clean_text("   ") is None


def test_clean_list_deduplicates():
    result = TextCleaner.clean_list(["Python", "Python", "Java"])
    assert result == ["Python", "Java"]


def test_clean_list_removes_empty():
    result = TextCleaner.clean_list(["", "  ", "Go"])
    assert result == ["Go"]


def test_clean_field_returns_empty_on_none():
    assert TextCleaner.clean_field(None) == ""


def test_remove_html_tags():
    assert TextCleaner.remove_html_tags("<p>Test</p>") == "Test"


def test_decode_html_entities():
    assert TextCleaner.decode_html_entities("&lt;div&gt;") == "<div>"
