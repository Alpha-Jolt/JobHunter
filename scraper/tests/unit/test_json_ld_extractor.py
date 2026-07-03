"""Unit tests for JSON-LD extractor."""

import pytest

from scraper.sources.career_page.extractors.json_ld_extractor import JSONLDExtractor

_COMPANY = {
    "company_id": "test-company-uuid",
    "apex_domain": "acme.com",
    "career_page_url": "https://acme.com/careers",
    "ats_platform": "custom",
}

SINGLE_JOB_POSTING_HTML = """
<html><head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "Senior Python Developer",
  "description": "We are looking for a Python developer with 3+ years experience.",
  "datePosted": "2026-07-01",
  "url": "https://acme.com/careers/jobs/python-dev",
  "jobLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Bangalore"
    }
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "INR",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 1200000,
      "maxValue": 1800000
    }
  },
  "employmentType": "FULL_TIME"
}
</script>
</head><body><h1>Careers</h1></body></html>
"""

MULTIPLE_JOBS_HTML = """
<html><head>
<script type="application/ld+json">
[
  {
    "@type": "JobPosting",
    "title": "Frontend Engineer",
    "url": "https://acme.com/careers/frontend",
    "description": "React.js experience required."
  },
  {
    "@type": "JobPosting",
    "title": "Backend Engineer",
    "url": "https://acme.com/careers/backend",
    "description": "Python and Django experience required."
  }
]
</script>
</head><body></body></html>
"""

NO_JOB_POSTING_HTML = """
<html><head>
<script type="application/ld+json">
{"@type": "Organization", "name": "Acme Corp"}
</script>
</head><body><h1>About Us</h1></body></html>
"""


class TestJSONLDExtractor:
    def setup_method(self):
        self.extractor = JSONLDExtractor()

    def test_extracts_single_job_posting(self):
        jobs = self.extractor._parse_json_ld(SINGLE_JOB_POSTING_HTML, _COMPANY)
        assert len(jobs) == 1
        job = jobs[0]
        assert job["job_title"] == "Senior Python Developer"
        assert "Python developer" in job["description"]
        assert job["location"] == "Bangalore"
        assert job["salary_min"] == 1200000
        assert job["salary_max"] == 1800000
        assert job["job_type"] == "fulltime"
        assert job["extraction_method"] == "json_ld"

    def test_extracts_multiple_job_postings(self):
        jobs = self.extractor._parse_json_ld(MULTIPLE_JOBS_HTML, _COMPANY)
        assert len(jobs) == 2
        titles = {j["job_title"] for j in jobs}
        assert "Frontend Engineer" in titles
        assert "Backend Engineer" in titles

    def test_no_job_postings_returns_empty(self):
        jobs = self.extractor._parse_json_ld(NO_JOB_POSTING_HTML, _COMPANY)
        assert jobs == []

    def test_missing_title_skipped(self):
        html = """
        <script type="application/ld+json">
        {"@type": "JobPosting", "description": "No title here"}
        </script>
        """
        jobs = self.extractor._parse_json_ld(html, _COMPANY)
        assert jobs == []

    def test_job_url_populated(self):
        jobs = self.extractor._parse_json_ld(SINGLE_JOB_POSTING_HTML, _COMPANY)
        assert jobs[0]["job_url"] == "https://acme.com/careers/jobs/python-dev"

    def test_company_id_set(self):
        jobs = self.extractor._parse_json_ld(SINGLE_JOB_POSTING_HTML, _COMPANY)
        assert jobs[0]["company_id"] == "test-company-uuid"

    def test_invalid_json_ld_skipped(self):
        html = """
        <script type="application/ld+json">not valid json{</script>
        """
        jobs = self.extractor._parse_json_ld(html, _COMPANY)
        assert jobs == []
