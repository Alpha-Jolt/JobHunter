"""E2E test — full pipeline with mock data (no live network calls)."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from scraper.cleaning.cleaner_pipeline import CleanerPipeline
from scraper.config import Config
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.deduplication.deduplicator import Deduplicator
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.normalization.normalizer import JobNormalizer
from scraper.pipeline.pipeline import ScraperPipeline
from scraper.sources.base_scraper import BaseScraper


class _MockScraper(BaseScraper):
    def __init__(self):
        super().__init__(RateLimiter(), RetryHandler(max_retries=0))

    async def scrape(self, keywords, locations, **kwargs):
        return [
            IntermediateJob(
                source="mock",
                external_id=f"job_{i}",
                raw_url=f"https://mock.com/job/{i}",
                title=f"Python Developer {i}",
                company_name="Acme Corp",
                location_raw="Bangalore, Karnataka",
                salary_raw="5 LPA - 8 LPA",
                experience_raw="2-5 years",
                job_type_raw="Full Time",
                description="Python Django REST API development. " * 20,
                posted_date_raw="2 days ago",
                skills_required_raw=["Python", "Django"],
                apply_url=f"https://mock.com/apply/{i}",
                extraction_timestamp=datetime.now(timezone.utc),
            )
            for i in range(10)
        ]

    async def initialize(self):
        pass

    async def close(self):
        pass

    def get_source_name(self):
        return "mock"


@pytest.mark.asyncio
async def test_full_pipeline_produces_canonical_jobs(tmp_path):
    cfg = Config(output_dir=tmp_path, output_formats="json")
    pipeline = ScraperPipeline(cfg)
    scraper = _MockScraper()

    result = await pipeline.execute(scraper, ["Python"], ["Bangalore"])

    assert result.raw_jobs_count == 10
    assert result.final_jobs_count > 0
    assert result.final_jobs_count <= result.raw_jobs_count
    assert all(j.title.startswith("Python Developer") for j in result.jobs)


@pytest.mark.asyncio
async def test_full_pipeline_deduplicates(tmp_path):
    """Duplicate jobs (same external_id) should be removed."""
    cfg = Config(output_dir=tmp_path, output_formats="json")
    pipeline = ScraperPipeline(cfg)

    class _DupScraper(_MockScraper):
        async def scrape(self, keywords, locations, **kwargs):
            jobs = await super().scrape(keywords, locations)
            return jobs + jobs  # 20 jobs, all duplicates

    result = await pipeline.execute(_DupScraper(), ["Python"], ["Bangalore"])
    assert result.duplicates_removed == 10
    assert result.final_jobs_count == 10
