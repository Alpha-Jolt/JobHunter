"""Baseline — marks existing schema (001_init_schema.sql + 002_auth_schema.sql) as applied.

This is a no-op migration. The schema already exists in the database from the
original SQL migration files. This revision marks those tables as the starting
point for all future Alembic-managed migrations.

To apply to an existing database without re-running the SQL:
    alembic stamp 0001_baseline

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-03
"""
from typing import Sequence, Union

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Schema already exists from 001_init_schema.sql and 002_auth_schema.sql.
    # No DDL changes — this revision is a baseline marker only.
    pass


def downgrade() -> None:
    # Cannot downgrade past the baseline — original SQL files are the source of truth.
    pass
