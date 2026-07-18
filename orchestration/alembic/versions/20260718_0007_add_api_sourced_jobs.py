"""Add api_sourced_jobs table for Apify/Hunter sourced listings.

Revision ID: 0007_add_api_sourced_jobs
Revises: 0006_add_mailbridge_tracking
Create Date: 2026-07-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_add_api_sourced_jobs"
down_revision: Union[str, None] = "0006_add_mailbridge_tracking"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "api_sourced_jobs" in inspector.get_table_names():
        return

    op.create_table(
        "api_sourced_jobs",
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.company_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_actor_id", sa.String(255), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("company_domain", sa.String(255), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("remote_type", sa.String(20), nullable=True),
        sa.Column("salary_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("experience_min", sa.Integer(), nullable=True),
        sa.Column("experience_max", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "skills_required",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("job_type", sa.String(20), nullable=True),
        sa.Column("apply_email", sa.String(255), nullable=True),
        sa.Column(
            "email_trust",
            sa.String(20),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="raw",
            nullable=False,
        ),
        sa.Column(
            "extra_data",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "source", "external_id", name="api_jobs_source_external_id_unique"
        ),
    )
    op.create_index(
        "ix_api_sourced_jobs_status_last_seen",
        "api_sourced_jobs",
        ["status", "last_seen_at"],
    )
    op.create_index(
        "ix_api_sourced_jobs_source",
        "api_sourced_jobs",
        ["source"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "api_sourced_jobs" not in inspector.get_table_names():
        return
    op.drop_index("ix_api_sourced_jobs_source", table_name="api_sourced_jobs")
    op.drop_index(
        "ix_api_sourced_jobs_status_last_seen", table_name="api_sourced_jobs"
    )
    op.drop_table("api_sourced_jobs")
