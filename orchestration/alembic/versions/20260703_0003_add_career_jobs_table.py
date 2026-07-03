"""Add career_jobs table for Module 2: Career Page Job Scraper.

Revision ID: 0003_add_career_jobs
Revises: 0002_add_companies
Create Date: 2026-07-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_add_career_jobs"
down_revision: Union[str, None] = "0002_add_companies"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "career_jobs",
        sa.Column(
            "career_job_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("job_title", sa.String(500), nullable=False),
        sa.Column("job_url", sa.Text(), nullable=False),
        sa.Column("url_hash", sa.String(64), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "skills_required",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("remote_type", sa.String(20), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("experience_min", sa.Integer(), nullable=True),
        sa.Column("experience_max", sa.Integer(), nullable=True),
        sa.Column("job_type", sa.String(20), nullable=True),
        sa.Column("apply_email", sa.String(255), nullable=True),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column("ats_platform", sa.String(50), nullable=True),
        sa.Column("extraction_method", sa.String(30), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="raw",
            nullable=False,
        ),
        sa.Column(
            "source_channel",
            sa.String(30),
            server_default="career_page",
            nullable=False,
        ),
        # Constraints
        sa.UniqueConstraint(
            "company_id", "url_hash", name="career_jobs_company_url_unique"
        ),
        sa.CheckConstraint(
            "remote_type IS NULL OR remote_type IN ('onsite','hybrid','remote')",
            name="ck_career_jobs_remote_type",
        ),
        sa.CheckConstraint(
            "job_type IS NULL OR job_type IN ('fulltime','parttime','contract','internship','freelance')",
            name="ck_career_jobs_job_type",
        ),
        sa.CheckConstraint(
            "extraction_method IN ('ats_api','json_ld','sitemap','api_reverse','html_parse','playwright_render')",
            name="ck_career_jobs_extraction_method",
        ),
        sa.CheckConstraint(
            "status IN ('active','closed','raw')",
            name="ck_career_jobs_status",
        ),
        sa.CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max",
            name="ck_career_jobs_salary_range",
        ),
    )

    # Indexes
    op.create_index("idx_career_jobs_company_id", "career_jobs", ["company_id"])
    op.create_index("idx_career_jobs_status", "career_jobs", ["status"])
    op.create_index("idx_career_jobs_url_hash", "career_jobs", ["url_hash"])
    op.create_index("idx_career_jobs_last_seen", "career_jobs", ["last_seen_at"])
    op.create_index("idx_career_jobs_scraped_at", "career_jobs", ["scraped_at"])
    op.create_index("idx_career_jobs_ats_platform", "career_jobs", ["ats_platform"])


def downgrade() -> None:
    op.drop_index("idx_career_jobs_ats_platform", table_name="career_jobs")
    op.drop_index("idx_career_jobs_scraped_at", table_name="career_jobs")
    op.drop_index("idx_career_jobs_last_seen", table_name="career_jobs")
    op.drop_index("idx_career_jobs_url_hash", table_name="career_jobs")
    op.drop_index("idx_career_jobs_status", table_name="career_jobs")
    op.drop_index("idx_career_jobs_company_id", table_name="career_jobs")
    op.drop_table("career_jobs")
