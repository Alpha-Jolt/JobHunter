"""Unit tests for JobNormalizer."""

from datetime import datetime

import pytest

from scraper.cleaning.cleaner_pipeline import CleanedJob, JobType, RemoteType
from scraper.normalization.normalizer import JobNormalizer


def _make_cleaned_job(**overrides) -> CleanedJob:
    defaults = dict(
        title="Python Developer",
        company_name="Acme Corp",
        location_raw="Bangalore, Karnataka",
        location_city="Bangalore",
        location_state="Karnataka",
        remote_type=RemoteType.ONSITE,
        salary_min_inr=500_000,
        salary_max_inr=800_000,
        salary_currency="INR",
        salary_raw="5-8 LPA",
        experience_min_years=2,
        experience_max_years=5,
        experience_raw="2-5 years",
        job_type=JobType.FULL_TIME,
        job_type_raw="Full Time",
        posted_date=datetime(2026, 4, 20),
        posted_date_raw="20/04/2026",
        description="We need a Python developer with Django experience. " * 20,
        skills_required=["Python", "Django"],
        benefits=["Health Insurance"],
        apply_url="https://example.com/apply",
        apply_email=None,
        company_domain="acme.com",
        source="naukri",
        external_id="12345",
        raw_url="https://naukri.com/job/12345",
    )
    defaults.update(overrides)
    return CleanedJob(**defaults)


def test_normalize_produces_canonical_job():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job())
    assert canonical.title == "Python Developer"
    assert canonical.source == "naukri"
    assert canonical.external_id == "12345"


def test_completeness_score_high():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job())
    assert canonical.completeness_score > 0.7


def test_confidence_score_high():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job())
    assert canonical.confidence_score > 0.5


def test_content_hash_generated():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job())
    assert len(canonical.content_hash) == 16


def test_apply_method_url():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job())
    assert canonical.apply_method == "url"


def test_apply_method_email():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job(apply_url=None, apply_email="hr@acme.com"))
    assert canonical.apply_method == "email"


def test_posted_days_ago():
    normalizer = JobNormalizer()
    canonical = normalizer.normalize(_make_cleaned_job())
    assert canonical.posted_days_ago is not None and canonical.posted_days_ago >= 0
