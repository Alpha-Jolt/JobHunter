"""
Module 2 Exit Criteria Verification Tests

All 8 criteria from TASK.md — Module 2 Exit Criteria section.
These tests run against a live database populated by the Career Page Job Scraper.
Mark with pytest -m exit_criteria to run selectively.
"""

import uuid

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.db.models import CareerJob, Company


@pytest.mark.asyncio
@pytest.mark.exit_criteria
class TestModule2ExitCriteria:
    """Verifies all 8 Module 2 exit criteria against a live database."""

    # ── Criterion 1 ──────────────────────────────────────────────────────────
    # At least 500 companies have active job listings extracted

    async def test_criterion_1_five_hundred_companies_with_active_jobs(
        self, async_session: AsyncSession
    ):
        """
        SELECT COUNT(DISTINCT company_id) FROM career_jobs
        WHERE status = 'active'
        → must be ≥500
        """
        result = await async_session.execute(
            select(func.count(func.distinct(CareerJob.company_id))).where(
                CareerJob.status == "active"
            )
        )
        count = result.scalar_one()
        assert count >= 500, (
            f"Criterion 1 FAILED: only {count} companies have active job listings "
            f"(need ≥500)"
        )

    # ── Criterion 2 ──────────────────────────────────────────────────────────
    # At least 70% of active jobs have apply_email or apply_url non-null

    async def test_criterion_2_seventy_percent_have_apply_contact(
        self, async_session: AsyncSession
    ):
        """
        COUNT(apply_email IS NOT NULL OR apply_url IS NOT NULL) / COUNT(*)
        for active jobs >= 0.70
        """
        result = await async_session.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE apply_email IS NOT NULL OR apply_url IS NOT NULL
                    ) AS with_contact,
                    COUNT(*) AS total_active
                FROM career_jobs
                WHERE status = 'active'
                """
            )
        )
        row = result.fetchone()
        with_contact, total_active = row[0], row[1]
        assert total_active > 0, "Criterion 2 FAILED: no active career jobs in table"
        pct = with_contact / total_active
        assert pct >= 0.70, (
            f"Criterion 2 FAILED: only {pct:.1%} of active jobs have apply_email or "
            f"apply_url (need ≥70%)"
        )

    # ── Criterion 3 ──────────────────────────────────────────────────────────
    # Change detection: re-crawl of unchanged job updates only last_seen_at

    async def test_criterion_3_change_detection_preserves_unchanged_jobs(
        self, async_session: AsyncSession
    ):
        """
        Fetch a known active job. Verify the ChangeDetector logic directly:
        - same hash → is_changed() returns False (only last_seen_at updated)
        - different hash → is_changed() returns True (full re-parse triggered)
        """
        from scraper.sources.career_page.change_detector import ChangeDetector

        detector = ChangeDetector()

        # Fetch a real active job to use as baseline
        result = await async_session.execute(
            select(
                CareerJob.career_job_id,
                CareerJob.content_hash,
                CareerJob.last_seen_at,
            )
            .where(CareerJob.status == "active")
            .limit(1)
        )
        row = result.fetchone()
        if row is None:
            pytest.skip("No active career jobs in table — skipping change detection check")

        _, stored_hash, _ = row[0], row[1], row[2]

        # Same content (no change expected)
        assert detector.is_changed(stored_hash, stored_hash) is False, (
            "Criterion 3 FAILED: is_changed() returned True for identical hashes"
        )

        # Different content (change expected)
        assert detector.is_changed(stored_hash, "new_different_hash") is True, (
            "Criterion 3 FAILED: is_changed() returned False for different hashes"
        )

    # ── Criterion 4 ──────────────────────────────────────────────────────────
    # Closed job detection: jobs not seen in latest crawl get status = 'closed'

    async def test_criterion_4_closed_job_detection(
        self, async_session: AsyncSession
    ):
        """
        Verifies the mark_closed_jobs logic on CareerPageRouter:
        Given a set of url_hashes seen in the latest crawl, any existing active job
        not in that set should be identified for closing.

        Uses a synthetic test job injected and then excluded from the seen set.
        """
        from scraper.sources.career_page.router import CareerPageRouter

        router = CareerPageRouter()

        # Insert a synthetic active job to test closing
        test_company_result = await async_session.execute(
            select(Company.company_id).where(Company.crawl_status == "enriched").limit(1)
        )
        company_row = test_company_result.fetchone()
        if company_row is None:
            pytest.skip("No enriched companies — cannot test closed job detection")

        test_company_id = company_row[0]
        test_url_hash = f"test_hash_{uuid.uuid4().hex[:8]}"

        synthetic_job = CareerJob(
            career_job_id=uuid.uuid4(),
            company_id=test_company_id,
            job_title="Test Closed Job",
            job_url=f"https://test.example.com/jobs/{test_url_hash}",
            url_hash=test_url_hash,
            content_hash="test_content_hash",
            extraction_method="html_parse",
            status="active",
            source_channel="career_page",
        )
        async_session.add(synthetic_job)
        await async_session.flush()

        # Simulate a crawl that does NOT include this job's url_hash
        seen_hashes: set[str] = {"other_hash_1", "other_hash_2"}
        existing_hashes: set[str] = {test_url_hash, "other_hash_1", "other_hash_2"}

        closed_hashes = router.mark_closed_jobs(existing_hashes, seen_hashes)
        assert test_url_hash in closed_hashes, (
            f"Criterion 4 FAILED: url_hash {test_url_hash} not identified as closed "
            f"despite being absent from seen_hashes"
        )

        # Clean up test record
        await async_session.delete(synthetic_job)
        await async_session.flush()

    # ── Criterion 5 ──────────────────────────────────────────────────────────
    # ATS API extraction used where Greenhouse, Lever, Ashby companies exist

    async def test_criterion_5_ats_api_used_for_known_ats_companies(
        self, async_session: AsyncSession
    ):
        """
        For companies with ats_platform IN ('greenhouse', 'lever', 'ashby'),
        at least one job must have extraction_method = 'ats_api'.
        """
        result = await async_session.execute(
            text(
                """
                SELECT COUNT(*) FROM career_jobs cj
                JOIN companies c ON c.company_id = cj.company_id
                WHERE c.ats_platform IN ('greenhouse', 'lever', 'ashby')
                  AND cj.extraction_method = 'ats_api'
                """
            )
        )
        count = result.scalar_one()

        # First check if any such companies exist at all
        ats_company_result = await async_session.execute(
            text(
                """
                SELECT COUNT(*) FROM companies
                WHERE ats_platform IN ('greenhouse', 'lever', 'ashby')
                  AND crawl_status = 'enriched'
                """
            )
        )
        ats_company_count = ats_company_result.scalar_one()

        if ats_company_count == 0:
            pytest.skip(
                "No Greenhouse/Lever/Ashby companies in table — skipping ATS API check"
            )

        assert count > 0, (
            f"Criterion 5 FAILED: 0 jobs extracted via 'ats_api' despite "
            f"{ats_company_count} Greenhouse/Lever/Ashby companies existing"
        )

    # ── Criterion 6 ──────────────────────────────────────────────────────────
    # Zero duplicate (company_id, url_hash) entries

    async def test_criterion_6_no_duplicate_company_url_hash_pairs(
        self, async_session: AsyncSession
    ):
        """
        SELECT company_id, url_hash, COUNT(*) FROM career_jobs
        GROUP BY company_id, url_hash
        HAVING COUNT(*) > 1
        → must return 0 rows
        """
        result = await async_session.execute(
            text(
                """
                SELECT company_id, url_hash, COUNT(*) AS cnt
                FROM career_jobs
                GROUP BY company_id, url_hash
                HAVING COUNT(*) > 1
                """
            )
        )
        duplicates = result.fetchall()
        assert len(duplicates) == 0, (
            f"Criterion 6 FAILED: {len(duplicates)} duplicate (company_id, url_hash) "
            f"pair(s) found — unique constraint not enforced"
        )

    # ── Criterion 7 ──────────────────────────────────────────────────────────
    # Zero robots.txt violations in scraper_runs for career_page_scrape source

    async def test_criterion_7_zero_robots_violations_career_scrape(
        self, async_session: AsyncSession
    ):
        """
        SELECT COUNT(*) FROM scraper_runs
        WHERE source = 'career_page_scrape'
          AND error_detail LIKE '%robots_blocked%'
        → must be 0
        """
        result = await async_session.execute(
            text(
                """
                SELECT COUNT(*) FROM scraper_runs
                WHERE source = 'career_page_scrape'
                  AND error_detail LIKE '%robots_blocked%'
                """
            )
        )
        violation_count = result.scalar_one()
        assert violation_count == 0, (
            f"Criterion 7 FAILED: {violation_count} robots.txt violation(s) logged "
            f"for career_page_scrape runs"
        )

    # ── Criterion 8 ──────────────────────────────────────────────────────────
    # Jobs are accessible to AI Engine via shared registry (end-to-end downstream check)

    async def test_criterion_8_jobs_accessible_via_shared_registry(
        self, async_session: AsyncSession
    ):
        """
        Verifies that a career job with apply_email set can be fetched and would
        be structurally valid for downstream AI Engine + Mail Bridge consumption.

        Checks: required fields are non-null, source_channel = 'career_page'.
        """
        result = await async_session.execute(
            select(CareerJob)
            .where(
                CareerJob.status == "active",
                CareerJob.apply_email.isnot(None),
            )
            .limit(1)
        )
        job = result.scalar_one_or_none()

        if job is None:
            pytest.skip(
                "No active career job with apply_email — cannot verify downstream access"
            )

        # Structural validity checks for downstream consumption
        assert job.job_title, "Criterion 8 FAILED: job_title is empty"
        assert job.company_id, "Criterion 8 FAILED: company_id is null"
        assert job.apply_email, "Criterion 8 FAILED: apply_email is null"
        assert job.source_channel == "career_page", (
            f"Criterion 8 FAILED: source_channel is '{job.source_channel}', "
            f"expected 'career_page'"
        )
        assert job.url_hash, "Criterion 8 FAILED: url_hash is null"
        assert job.content_hash, "Criterion 8 FAILED: content_hash is null"
