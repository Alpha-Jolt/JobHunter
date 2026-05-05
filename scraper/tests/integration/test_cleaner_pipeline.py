"""Integration tests for the cleaning pipeline."""

import pytest

from scraper.cleaning.cleaner_pipeline import CleanerPipeline
from scraper.extraction.intermediate_schema import IntermediateJob


def _make_intermediate(**overrides) -> IntermediateJob:
    defaults = dict(
        source="naukri",
        external_id="test_001",
        raw_url="https://naukri.com/job/test_001",
        title="  <b>Python Developer</b>  ",
        company_name="Acme Corp",
        location_raw="Bangalore, Karnataka",
        salary_raw="5 LPA - 8 LPA",
        experience_raw="2-5 years",
        job_type_raw="Full Time",
        description="We need a Python developer. " * 30,
        posted_date_raw="3 days ago",
        skills_required_raw=["Python", "Django", "Python"],
        benefits_raw=["Health Insurance"],
        apply_url="https://naukri.com/apply/test_001",
    )
    defaults.update(overrides)
    return IntermediateJob(**defaults)


@pytest.mark.asyncio
async def test_clean_produces_cleaned_job():
    pipeline = CleanerPipeline()
    cleaned = await pipeline.clean(_make_intermediate())
    assert cleaned.title == "Python Developer"
    assert cleaned.company_name == "Acme Corp"


@pytest.mark.asyncio
async def test_clean_deduplicates_skills():
    pipeline = CleanerPipeline()
    cleaned = await pipeline.clean(_make_intermediate())
    assert cleaned.skills_required.count("Python") == 1


@pytest.mark.asyncio
async def test_clean_parses_salary():
    pipeline = CleanerPipeline()
    cleaned = await pipeline.clean(_make_intermediate())
    assert cleaned.salary_min_inr == 500_000
    assert cleaned.salary_max_inr == 800_000


@pytest.mark.asyncio
async def test_clean_parses_experience():
    pipeline = CleanerPipeline()
    cleaned = await pipeline.clean(_make_intermediate())
    assert cleaned.experience_min_years == 2
    assert cleaned.experience_max_years == 5


@pytest.mark.asyncio
async def test_clean_records_steps():
    pipeline = CleanerPipeline()
    cleaned = await pipeline.clean(_make_intermediate())
    assert "title" in cleaned.cleaning_steps_applied
    assert "salary" in cleaned.cleaning_steps_applied
