"""Add companies table for Module 1: Company Discovery Scraper.

Revision ID: 0002_add_companies
Revises: 0001_baseline
Create Date: 2026-07-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_add_companies"
down_revision: Union[str, None] = "0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("company_name", sa.String(500), nullable=True),
        sa.Column("normalized_name", sa.String(500), nullable=True),
        sa.Column("apex_domain", sa.String(255), nullable=False),
        sa.Column(
            "subdomains",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("career_page_url", sa.Text(), nullable=True),
        sa.Column(
            "career_emails",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "contact_emails",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "email_trust",
            sa.String(20),
            server_default="unverified",
            nullable=False,
        ),
        sa.Column(
            "ats_platform",
            sa.String(50),
            server_default="none",
            nullable=False,
        ),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("hq_location", sa.String(255), nullable=True),
        sa.Column("company_size", sa.String(50), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_detail", sa.Text(), nullable=True),
        sa.Column("robots_txt_allowed", sa.Boolean(), nullable=True),
        sa.Column(
            "discovery_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_enriched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email_last_crawled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "crawl_status",
            sa.String(20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("dedup_fingerprint", sa.String(64), nullable=False),
        sa.Column(
            "related_company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Constraints
        sa.UniqueConstraint("apex_domain", name="companies_apex_domain_unique"),
        sa.UniqueConstraint("dedup_fingerprint", name="companies_dedup_fingerprint_unique"),
        sa.CheckConstraint(
            "email_trust IN ('unverified', 'low_trust')",
            name="ck_companies_email_trust",
        ),
        sa.CheckConstraint(
            "ats_platform IN ('greenhouse','lever','ashby','workday','smartrecruiters',"
            "'bamboohr','teamtailor','recruitee','jazzhr','workable','custom','none')",
            name="ck_companies_ats_platform",
        ),
        sa.CheckConstraint(
            "crawl_status IN ('pending','enriched','failed','robots_blocked','access_denied','name_only')",
            name="ck_companies_crawl_status",
        ),
        sa.CheckConstraint(
            "source IN ('bootstrap_dataset','govt_registry','vc_portfolio','github_org',"
            "'directory','search_discovery','recursive')",
            name="ck_companies_source",
        ),
    )

    # Indexes
    op.create_index("idx_companies_apex_domain", "companies", ["apex_domain"])
    op.create_index("idx_companies_crawl_status", "companies", ["crawl_status"])
    op.create_index("idx_companies_source", "companies", ["source"])
    op.create_index("idx_companies_ats_platform", "companies", ["ats_platform"])
    op.create_index(
        "idx_companies_email_last_crawled",
        "companies",
        ["email_last_crawled_at"],
    )
    op.create_index("idx_companies_discovery_date", "companies", ["discovery_date"])


def downgrade() -> None:
    op.drop_index("idx_companies_discovery_date", table_name="companies")
    op.drop_index("idx_companies_email_last_crawled", table_name="companies")
    op.drop_index("idx_companies_ats_platform", table_name="companies")
    op.drop_index("idx_companies_source", table_name="companies")
    op.drop_index("idx_companies_crawl_status", table_name="companies")
    op.drop_index("idx_companies_apex_domain", table_name="companies")
    op.drop_table("companies")
