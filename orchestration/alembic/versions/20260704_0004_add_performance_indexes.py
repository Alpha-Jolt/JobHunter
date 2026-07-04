"""Add performance indexes to companies and career_jobs tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-04
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003_add_career_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── companies indexes ─────────────────────────────────────────────────────
    op.create_index("idx_companies_crawl_status", "companies", ["crawl_status"])
    op.create_index("idx_companies_source", "companies", ["source"])
    op.create_index("idx_companies_ats_platform", "companies", ["ats_platform"])
    op.create_index("idx_companies_email_last_crawled", "companies", ["email_last_crawled_at"])
    op.create_index("idx_companies_discovery_date", "companies", ["discovery_date"])
    op.create_index("idx_companies_robots_allowed", "companies", ["robots_txt_allowed"])

    # ── career_jobs indexes ───────────────────────────────────────────────────
    op.create_index("idx_career_jobs_company_id", "career_jobs", ["company_id"])
    op.create_index("idx_career_jobs_status", "career_jobs", ["status"])
    op.create_index("idx_career_jobs_url_hash", "career_jobs", ["url_hash"])
    op.create_index("idx_career_jobs_last_seen", "career_jobs", ["last_seen_at"])
    op.create_index("idx_career_jobs_scraped_at", "career_jobs", ["scraped_at"])
    op.create_index("idx_career_jobs_ats_platform", "career_jobs", ["ats_platform"])


def downgrade() -> None:
    # ── career_jobs indexes ───────────────────────────────────────────────────
    op.drop_index("idx_career_jobs_ats_platform", table_name="career_jobs")
    op.drop_index("idx_career_jobs_scraped_at", table_name="career_jobs")
    op.drop_index("idx_career_jobs_last_seen", table_name="career_jobs")
    op.drop_index("idx_career_jobs_url_hash", table_name="career_jobs")
    op.drop_index("idx_career_jobs_status", table_name="career_jobs")
    op.drop_index("idx_career_jobs_company_id", table_name="career_jobs")

    # ── companies indexes ─────────────────────────────────────────────────────
    op.drop_index("idx_companies_robots_allowed", table_name="companies")
    op.drop_index("idx_companies_discovery_date", table_name="companies")
    op.drop_index("idx_companies_email_last_crawled", table_name="companies")
    op.drop_index("idx_companies_ats_platform", table_name="companies")
    op.drop_index("idx_companies_source", table_name="companies")
    op.drop_index("idx_companies_crawl_status", table_name="companies")
