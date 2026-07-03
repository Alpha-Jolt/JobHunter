"""Unit tests for ATS detector — all 10 platform patterns and custom fallback."""

import pytest

from scraper.sources.company_discovery.enrichment.ats_detector import (
    ATS_PATTERNS,
    detect_ats_from_html,
    extract_ats_slug,
)


class TestDetectAtsFromHtml:
    def test_detects_greenhouse(self):
        html = '<a href="https://boards.greenhouse.io/acmecorp/jobs/123">Apply</a>'
        assert detect_ats_from_html(html) == "greenhouse"

    def test_detects_lever(self):
        html = '<iframe src="https://jobs.lever.co/acme"></iframe>'
        assert detect_ats_from_html(html) == "lever"

    def test_detects_ashby(self):
        html = '<script src="https://jobs.ashby.com/acme/widget.js"></script>'
        assert detect_ats_from_html(html) == "ashby"

    def test_detects_workday(self):
        html = '<a href="https://acme.myworkdayjobs.com/careers">Careers</a>'
        assert detect_ats_from_html(html) == "workday"

    def test_detects_smartrecruiters(self):
        html = '<a href="https://jobs.smartrecruiters.com/Acme">Jobs</a>'
        assert detect_ats_from_html(html) == "smartrecruiters"

    def test_detects_bamboohr(self):
        html = '<form action="https://acme.bamboohr.com/careers">Submit</form>'
        assert detect_ats_from_html(html) == "bamboohr"

    def test_detects_teamtailor(self):
        html = '<script src="https://acme.teamtailor.com/jobs.js"></script>'
        assert detect_ats_from_html(html) == "teamtailor"

    def test_detects_recruitee(self):
        html = '<a href="https://acme.recruitee.com/apply">Apply Now</a>'
        assert detect_ats_from_html(html) == "recruitee"

    def test_detects_jazzhr(self):
        html = '<a href="https://app.jazzhr.com/jobs/acme">Open roles</a>'
        assert detect_ats_from_html(html) == "jazzhr"

    def test_detects_workable(self):
        html = '<a href="https://apply.workable.com/acme/">Apply</a>'
        assert detect_ats_from_html(html) == "workable"

    def test_returns_custom_for_unknown(self):
        html = "<html><body><h1>Our Team</h1><a href='/jobs'>Careers</a></body></html>"
        assert detect_ats_from_html(html) == "custom"

    def test_case_insensitive(self):
        html = '<a href="HTTPS://BOARDS.GREENHOUSE.IO/ACME">Apply</a>'
        assert detect_ats_from_html(html) == "greenhouse"

    def test_ats_patterns_covers_all_platforms(self):
        expected_platforms = {
            "greenhouse", "lever", "ashby", "workday", "smartrecruiters",
            "bamboohr", "teamtailor", "recruitee", "jazzhr", "workable",
        }
        assert set(ATS_PATTERNS.keys()) == expected_platforms


class TestExtractAtsSlug:
    def test_greenhouse_boards_url(self):
        slug = extract_ats_slug("greenhouse", "https://boards.greenhouse.io/acmecorp")
        assert slug == "acmecorp"

    def test_lever_jobs_url(self):
        slug = extract_ats_slug("lever", "https://jobs.lever.co/acme-inc")
        assert slug == "acme-inc"

    def test_ashby_jobs_url(self):
        slug = extract_ats_slug("ashby", "https://jobs.ashby.com/my-company")
        assert slug == "my-company"

    def test_unsupported_platform_returns_none(self):
        slug = extract_ats_slug("workday", "https://acme.myworkdayjobs.com/careers")
        assert slug is None

    def test_url_with_trailing_path(self):
        slug = extract_ats_slug("greenhouse", "https://boards.greenhouse.io/acmecorp/jobs/123")
        assert slug == "acmecorp"

    def test_empty_url_returns_none(self):
        slug = extract_ats_slug("greenhouse", "")
        assert slug is None
