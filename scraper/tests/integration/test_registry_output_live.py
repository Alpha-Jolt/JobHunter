"""Live integration tests for scraper → JobRegistry write."""

import pytest
from shared.registries.job_registry import JobRegistry
from shared.models.job_record import JobRecord


@pytest.fixture
async def isolated_job_registry(tmp_path):
    """Isolated JobRegistry backed by a temp file."""
    registry = JobRegistry(file_path=str(tmp_path / "test_jobs.json"))
    yield registry


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scraper_writes_jobs_to_registry(isolated_job_registry):
    """Verify scraper pipeline writes jobs to JobRegistry with required fields.

    Validates:
    1. Scraper produces jobs
    2. Jobs are written to isolated JobRegistry
    3. Required fields are populated
    4. Deduplication prevents duplicate writes
    """
    from scraper.scraper.core.browser_manager import BrowserManager
    from scraper.scraper.core.rate_limiter import RateLimiter
    from scraper.scraper.core.retry_handler import RetryHandler
    from scraper.scraper.sources.naukri_scraper import NaukriScraper
    from scraper.scraper.cleaning.cleaner_pipeline import CleanerPipeline
    from scraper.scraper.normalization.normalizer import Normalizer
    from scraper.scraper.deduplication.deduplicator import Deduplicator

    browser_manager = BrowserManager()
    await browser_manager.initialize()

    try:
        scraper = NaukriScraper(
            browser_manager=browser_manager,
            rate_limiter=RateLimiter(),
            retry_handler=RetryHandler(),
        )
        cleaner = CleanerPipeline()
        normalizer = Normalizer()
        deduplicator = Deduplicator()

        raw_jobs = await scraper.scrape(
            keywords=["Python Developer"],
            locations=["Bangalore"],
            pages=1,
        )
        assert len(raw_jobs) > 0, "Scraper returned no jobs"

        cleaned = [cleaner.clean(job) for job in raw_jobs]
        normalized = [normalizer.normalize(job) for job in cleaned]
        deduped = deduplicator.deduplicate(normalized)

        job_records = [JobRecord.from_dict(j.to_dict()) for j in deduped]
        await isolated_job_registry.save(job_records)

        all_jobs = await isolated_job_registry.get_all()
        assert len(all_jobs) >= 1

        for job in all_jobs:
            assert job.job_id, "job_id missing"
            assert job.source == "naukri", f"expected source 'naukri', got {job.source!r}"
            assert job.title, "title missing"
            assert job.company_name, "company_name missing"
            assert job.description, "description missing"

        # Second write of same records must not increase count (deduplication)
        count_before = len(all_jobs)
        await isolated_job_registry.save(job_records)
        all_jobs_after = await isolated_job_registry.get_all()
        assert len(all_jobs_after) == count_before, "Deduplication failed"

    finally:
        await browser_manager.close_all()
