"""
Module 1 Exit Criteria Verification Tests

All 8 criteria from TASK.md — Module 1 Exit Criteria section.
These tests run against a live database populated by the Company Discovery scraper.
Mark with pytest -m exit_criteria to run selectively.
"""

import re
import uuid

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.db.models import Company


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


@pytest.mark.asyncio
@pytest.mark.exit_criteria
class TestModule1ExitCriteria:
    """Verifies all 8 Module 1 exit criteria against a live database."""

    # ── Criterion 1 ──────────────────────────────────────────────────────────
    # 1,000 companies in companies table with crawl_status = 'enriched'

    async def test_criterion_1_thousand_enriched_companies(
        self, async_session: AsyncSession
    ):
        """SELECT COUNT(*) FROM companies WHERE crawl_status = 'enriched' >= 1000"""
        result = await async_session.execute(
            select(func.count(Company.company_id)).where(
                Company.crawl_status == "enriched"
            )
        )
        count = result.scalar_one()
        assert count >= 1000, (
            f"Criterion 1 FAILED: expected ≥1000 enriched companies, got {count}"
        )

    # ── Criterion 2 ──────────────────────────────────────────────────────────
    # Zero duplicate apex_domain entries

    async def test_criterion_2_no_duplicate_apex_domains(
        self, async_session: AsyncSession
    ):
        """
        SELECT apex_domain, COUNT(*) FROM companies
        GROUP BY apex_domain HAVING COUNT(*) > 1
        → must return 0 rows
        """
        result = await async_session.execute(
            text(
                """
                SELECT apex_domain, COUNT(*) AS cnt
                FROM companies
                GROUP BY apex_domain
                HAVING COUNT(*) > 1
                """
            )
        )
        duplicates = result.fetchall()
        assert len(duplicates) == 0, (
            f"Criterion 2 FAILED: {len(duplicates)} duplicate apex_domain(s) found: "
            f"{[row[0] for row in duplicates[:5]]}"
        )

    # ── Criterion 3 ──────────────────────────────────────────────────────────
    # At least 60% of enriched companies have a career page URL

    async def test_criterion_3_sixty_percent_have_career_page_url(
        self, async_session: AsyncSession
    ):
        """
        COUNT(career_page_url IS NOT NULL) / COUNT(*) >= 0.60
        for enriched companies
        """
        result = await async_session.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (WHERE career_page_url IS NOT NULL) AS with_url,
                    COUNT(*) AS total
                FROM companies
                WHERE crawl_status = 'enriched'
                """
            )
        )
        row = result.fetchone()
        with_url, total = row[0], row[1]
        assert total > 0, "Criterion 3 FAILED: no enriched companies in table"
        pct = with_url / total
        assert pct >= 0.60, (
            f"Criterion 3 FAILED: only {pct:.1%} of enriched companies "
            f"have a career_page_url (need ≥60%)"
        )

    # ── Criterion 4 ──────────────────────────────────────────────────────────
    # At least 40% of enriched companies have at least one career email

    async def test_criterion_4_forty_percent_have_career_email(
        self, async_session: AsyncSession
    ):
        """
        COUNT(cardinality(career_emails) > 0) / COUNT(*) >= 0.40
        for enriched companies
        """
        result = await async_session.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (WHERE cardinality(career_emails) > 0) AS with_email,
                    COUNT(*) AS total
                FROM companies
                WHERE crawl_status = 'enriched'
                """
            )
        )
        row = result.fetchone()
        with_email, total = row[0], row[1]
        assert total > 0, "Criterion 4 FAILED: no enriched companies in table"
        pct = with_email / total
        assert pct >= 0.40, (
            f"Criterion 4 FAILED: only {pct:.1%} of enriched companies "
            f"have a career email (need ≥40%)"
        )

    # ── Criterion 5 ──────────────────────────────────────────────────────────
    # ATS platform detected for at least 50% of companies with a career page

    async def test_criterion_5_ats_detected_for_fifty_percent(
        self, async_session: AsyncSession
    ):
        """
        Among enriched companies with career_page_url:
        COUNT(ats_platform NOT IN ('none', 'custom')) / COUNT(*) >= 0.50
        """
        result = await async_session.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE ats_platform NOT IN ('none', 'custom')
                    ) AS with_known_ats,
                    COUNT(*) AS total_with_career_page
                FROM companies
                WHERE crawl_status = 'enriched'
                  AND career_page_url IS NOT NULL
                """
            )
        )
        row = result.fetchone()
        with_known_ats, total_with_career_page = row[0], row[1]
        assert total_with_career_page > 0, (
            "Criterion 5 FAILED: no enriched companies with career_page_url"
        )
        pct = with_known_ats / total_with_career_page
        assert pct >= 0.50, (
            f"Criterion 5 FAILED: ATS detected for only {pct:.1%} of companies "
            f"with a career page (need ≥50%)"
        )

    # ── Criterion 6 ──────────────────────────────────────────────────────────
    # Zero robots.txt violations in scraper_runs error log

    async def test_criterion_6_zero_robots_txt_violations(
        self, async_session: AsyncSession
    ):
        """
        SELECT COUNT(*) FROM scraper_runs
        WHERE source LIKE 'company_discovery%'
          AND error_detail LIKE '%robots_blocked%'
        → must be 0
        """
        result = await async_session.execute(
            text(
                """
                SELECT COUNT(*) FROM scraper_runs
                WHERE source LIKE 'company_discovery%'
                  AND error_detail LIKE '%robots_blocked%'
                """
            )
        )
        violation_count = result.scalar_one()
        assert violation_count == 0, (
            f"Criterion 6 FAILED: {violation_count} robots.txt violation(s) "
            f"logged in scraper_runs"
        )

    # ── Criterion 7 ──────────────────────────────────────────────────────────
    # Dedup fingerprint unique constraint holds — insert known duplicate is rejected

    async def test_criterion_7_dedup_fingerprint_unique_constraint(
        self, async_session: AsyncSession
    ):
        """
        Attempt inserting a company with the same dedup_fingerprint as an existing record.
        The unique constraint must reject it (IntegrityError or ON CONFLICT returns same row).
        """
        from sqlalchemy.exc import IntegrityError

        # Fetch any existing company to use its fingerprint
        result = await async_session.execute(
            select(Company.dedup_fingerprint, Company.apex_domain).limit(1)
        )
        row = result.fetchone()
        if row is None:
            pytest.skip("No companies in table — cannot test dedup constraint")

        existing_fp = row[0]

        # Attempt duplicate insert (different domain, same fingerprint)
        duplicate = Company(
            company_id=uuid.uuid4(),
            company_name="Duplicate Corp",
            normalized_name="duplicatecorp",
            apex_domain=f"duplicate-{uuid.uuid4().hex[:6]}.com",  # unique domain
            source="search_discovery",
            dedup_fingerprint=existing_fp,  # duplicate fingerprint
            crawl_status="pending",
        )
        async_session.add(duplicate)

        try:
            await async_session.flush()
            # If no error raised, the unique constraint is missing — fail
            pytest.fail(
                "Criterion 7 FAILED: duplicate dedup_fingerprint was accepted — "
                "unique constraint not enforced"
            )
        except IntegrityError:
            # Expected — unique constraint correctly rejected the duplicate
            await async_session.rollback()

    # ── Criterion 8 ──────────────────────────────────────────────────────────
    # All emails in career_emails are format-valid (sample 50 records)

    async def test_criterion_8_career_emails_are_format_valid(
        self, async_session: AsyncSession
    ):
        """
        Sample up to 50 enriched companies with career_emails.
        Validate every email address in each array matches the RFC format regex.
        """
        result = await async_session.execute(
            text(
                """
                SELECT company_id, career_emails
                FROM companies
                WHERE crawl_status = 'enriched'
                  AND cardinality(career_emails) > 0
                LIMIT 50
                """
            )
        )
        rows = result.fetchall()
        if not rows:
            pytest.skip("No enriched companies with career_emails — skipping format check")

        invalid: list[tuple[str, str]] = []
        for company_id, emails in rows:
            for email in (emails or []):
                if not EMAIL_RE.match(email):
                    invalid.append((str(company_id), email))

        assert len(invalid) == 0, (
            f"Criterion 8 FAILED: {len(invalid)} format-invalid email(s) found: "
            f"{invalid[:10]}"
        )
