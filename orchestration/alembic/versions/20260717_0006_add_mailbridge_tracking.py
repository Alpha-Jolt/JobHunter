"""Add user_mail_credentials table and mailbridge tracking columns.

Revision ID: 0006_add_mailbridge_tracking
Revises: 0005_add_is_generated
Create Date: 2026-07-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision: str = "0006_add_mailbridge_tracking"
down_revision: Union[str, None] = "0005_add_is_generated"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user_mail_credentials table ──────────────────────────────────────────
    op.create_table(
        "user_mail_credentials",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("mailbridge_credential_id", UUID(as_uuid=True), nullable=False),
        sa.Column("provider_type", sa.String(20), nullable=False, server_default="gmail"),
        sa.Column("from_email", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── mailbridge delivery tracking on application_logs ────────────────────
    op.add_column(
        "application_logs",
        sa.Column("mailbridge_email_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "application_logs",
        sa.Column(
            "email_delivery_status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
    )
    op.add_column(
        "application_logs",
        sa.Column("email_delivered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "idx_application_logs_mailbridge_email_id",
        "application_logs",
        ["mailbridge_email_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_application_logs_mailbridge_email_id",
        table_name="application_logs",
    )
    op.drop_column("application_logs", "email_delivered_at")
    op.drop_column("application_logs", "email_delivery_status")
    op.drop_column("application_logs", "mailbridge_email_id")
    op.drop_table("user_mail_credentials")
