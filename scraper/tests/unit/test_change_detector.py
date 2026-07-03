"""Unit tests for change detector and URL utilities."""

import pytest

from scraper.sources.career_page.change_detector import ChangeDetector
from scraper.sources.career_page.url_utils import (
    compute_content_hash,
    compute_url_hash,
    is_job_url,
    normalize_job_url,
)


class TestNormalizeJobUrl:
    def test_strips_tracking_params(self):
        url = "https://acme.com/jobs/123?utm_source=linkedin&utm_medium=social"
        assert "utm_source" not in normalize_job_url(url)
        assert "utm_medium" not in normalize_job_url(url)

    def test_keeps_non_tracking_params(self):
        url = "https://acme.com/jobs?page=2"
        assert "page=2" in normalize_job_url(url)

    def test_strips_trailing_slash(self):
        url = "https://acme.com/jobs/123/"
        assert not normalize_job_url(url).endswith("/")

    def test_lowercases(self):
        url = "https://ACME.COM/Jobs/123"
        assert normalize_job_url(url) == normalize_job_url(url).lower()

    def test_strips_gh_src(self):
        url = "https://boards.greenhouse.io/acme/jobs/1?gh_src=newsletter"
        assert "gh_src" not in normalize_job_url(url)

    def test_same_url_same_result(self):
        url = "https://acme.com/jobs/123"
        assert normalize_job_url(url) == normalize_job_url(url)


class TestComputeUrlHash:
    def test_returns_32_chars(self):
        h = compute_url_hash("https://acme.com/jobs/123")
        assert len(h) == 32

    def test_same_input_same_hash(self):
        assert compute_url_hash("https://acme.com/jobs/123") == compute_url_hash("https://acme.com/jobs/123")

    def test_different_url_different_hash(self):
        assert compute_url_hash("https://acme.com/jobs/1") != compute_url_hash("https://acme.com/jobs/2")


class TestComputeContentHash:
    def test_same_content_same_hash(self):
        h1 = compute_content_hash("Python Developer", "We need Python skills")
        h2 = compute_content_hash("Python Developer", "We need Python skills")
        assert h1 == h2

    def test_whitespace_normalised(self):
        h1 = compute_content_hash("Python  Developer", "We need Python  skills")
        h2 = compute_content_hash("Python Developer", "We need Python skills")
        assert h1 == h2

    def test_case_insensitive(self):
        h1 = compute_content_hash("PYTHON DEVELOPER", "WE NEED PYTHON SKILLS")
        h2 = compute_content_hash("python developer", "we need python skills")
        assert h1 == h2

    def test_different_content_different_hash(self):
        h1 = compute_content_hash("Python Developer", "Old description")
        h2 = compute_content_hash("Python Developer", "New description")
        assert h1 != h2


class TestIsJobUrl:
    def test_job_path(self):
        assert is_job_url("https://acme.com/job/123") is True

    def test_jobs_path(self):
        assert is_job_url("https://acme.com/jobs/python-dev") is True

    def test_position_path(self):
        assert is_job_url("https://acme.com/positions/12") is True

    def test_opening_path(self):
        assert is_job_url("https://acme.com/openings/456") is True

    def test_role_path(self):
        assert is_job_url("https://acme.com/roles/senior-dev") is True

    def test_non_job_path(self):
        assert is_job_url("https://acme.com/about") is False

    def test_homepage(self):
        assert is_job_url("https://acme.com/") is False


class TestChangeDetector:
    def setup_method(self):
        self.detector = ChangeDetector()

    def test_new_job_always_changed(self):
        assert self.detector.is_changed(None, "abc123") is True

    def test_same_hash_not_changed(self):
        assert self.detector.is_changed("abc123", "abc123") is False

    def test_different_hash_changed(self):
        assert self.detector.is_changed("abc123", "def456") is True

    def test_compute_hash_consistency(self):
        h1 = self.detector.compute_content_hash("Software Engineer", "We build software")
        h2 = self.detector.compute_content_hash("Software Engineer", "We build software")
        assert h1 == h2

    def test_compute_hash_differs_on_description_change(self):
        h1 = self.detector.compute_content_hash("Software Engineer", "Old description")
        h2 = self.detector.compute_content_hash("Software Engineer", "New description")
        assert h1 != h2
