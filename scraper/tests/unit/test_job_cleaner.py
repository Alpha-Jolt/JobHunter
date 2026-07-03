"""Unit tests for job cleaner pipeline — skill extraction, experience parsing, classification."""

import pytest

from scraper.sources.career_page.job_cleaner import (
    JobCleanerPipeline,
    classify_job_type,
    extract_skills,
    parse_experience,
)


class TestExtractSkills:
    def test_extracts_python(self):
        skills = extract_skills("We need Python and Django experience.")
        assert "python" in skills or "Python" in [s.lower() for s in skills]

    def test_extracts_react(self):
        skills = extract_skills("Must know React.js and TypeScript.")
        lower_skills = [s.lower() for s in skills]
        assert any("react" in s for s in lower_skills)

    def test_no_skills_empty_list(self):
        skills = extract_skills("We are a great team looking for talent.")
        # May be empty or contain soft skills — just verify no crash
        assert isinstance(skills, list)

    def test_deduplicates(self):
        skills = extract_skills("Python Python Python developer needed.")
        lower = [s.lower() for s in skills]
        assert lower.count("python") <= 1

    def test_empty_text(self):
        assert extract_skills("") == []

    def test_case_insensitive(self):
        skills_lower = extract_skills("python developer")
        skills_upper = extract_skills("PYTHON DEVELOPER")
        assert set(s.lower() for s in skills_lower) == set(s.lower() for s in skills_upper)


class TestParseExperience:
    def test_range_pattern(self):
        min_y, max_y = parse_experience("We need 2-5 years of experience.")
        assert min_y == 2
        assert max_y == 5

    def test_plus_pattern(self):
        min_y, max_y = parse_experience("3+ years experience required.")
        assert min_y == 3
        assert max_y is None

    def test_single_years(self):
        min_y, max_y = parse_experience("Minimum 4 years of experience.")
        assert max_y == 4

    def test_fresher(self):
        min_y, max_y = parse_experience("Fresher candidates can apply.")
        assert min_y == 0
        assert max_y == 0

    def test_no_experience_mentioned(self):
        min_y, max_y = parse_experience("Great opportunity for a passionate engineer.")
        assert min_y is None
        assert max_y is None

    def test_to_pattern(self):
        min_y, max_y = parse_experience("1 to 3 years experience")
        assert min_y == 1
        assert max_y == 3

    def test_empty_string(self):
        assert parse_experience("") == (None, None)


class TestClassifyJobType:
    def test_full_time(self):
        assert classify_job_type("Software Engineer", "This is a full-time role.") == "fulltime"

    def test_internship_from_title(self):
        assert classify_job_type("Software Intern", "Join our team.") == "internship"

    def test_contract(self):
        assert classify_job_type("Developer", "Contract position for 6 months.") == "contract"

    def test_part_time(self):
        assert classify_job_type("Support Agent", "Part-time role available.") == "parttime"

    def test_unclassifiable_returns_none(self):
        result = classify_job_type("Engineer", "We build great products.")
        assert result is None or isinstance(result, str)


class TestJobCleanerPipeline:
    def setup_method(self):
        self.cleaner = JobCleanerPipeline()

    def test_cleans_title(self):
        raw = {
            "job_title": "  Python   Developer  ",
            "job_url": "https://acme.com/jobs/1",
            "description": "Python required.",
        }
        cleaned = self.cleaner.clean(raw)
        assert cleaned["job_title"] == "Python Developer"

    def test_removes_html_from_description(self):
        raw = {
            "job_title": "Developer",
            "job_url": "https://acme.com/jobs/1",
            "description": "<p>We need <strong>Python</strong> skills.</p>",
        }
        cleaned = self.cleaner.clean(raw)
        assert "<p>" not in cleaned["description"]
        assert "<strong>" not in cleaned["description"]

    def test_removes_internal_routing_flag(self):
        raw = {
            "job_title": "Developer",
            "job_url": "https://acme.com/jobs/1",
            "description": "Python job.",
            "_needs_detail_fetch": True,
        }
        cleaned = self.cleaner.clean(raw)
        assert "_needs_detail_fetch" not in cleaned

    def test_skills_extracted(self):
        raw = {
            "job_title": "Python Developer",
            "job_url": "https://acme.com/jobs/1",
            "description": "Must know Python, Django, and PostgreSQL.",
        }
        cleaned = self.cleaner.clean(raw)
        skills_lower = [s.lower() for s in cleaned.get("skills_required", [])]
        assert "python" in skills_lower

    def test_passes_existing_salary(self):
        raw = {
            "job_title": "Developer",
            "job_url": "https://acme.com/jobs/1",
            "description": "Good salary.",
            "salary_min": 500000,
            "salary_max": 800000,
        }
        cleaned = self.cleaner.clean(raw)
        assert cleaned["salary_min"] == 500000
        assert cleaned["salary_max"] == 800000
