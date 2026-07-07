"""Add is_generated flag to companies table.

Revision ID: 0005_add_is_generated
Revises: 0004
Create Date: 2026-07-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_add_is_generated"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column(
            "is_generated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
    )
    op.create_index(
        "idx_companies_is_generated",
        "companies",
        ["is_generated"],
    )


def downgrade() -> None:
    op.drop_index("idx_companies_is_generated", table_name="companies")
    op.drop_column("companies", "is_generated")
