"""Alembic migration environment — async engine with SQLAlchemy models."""

import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Import Base so Alembic autogenerate can detect model changes.
# All models must be imported (directly or transitively) before this point.
from orchestration.db.models import Base  # noqa: F401 — triggers model registration

logger = logging.getLogger(__name__)

# Alembic Config object — provides access to alembic.ini values.
config = context.config

# Optionally interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support.
target_metadata = Base.metadata


def get_database_url() -> str:
    """Return the DATABASE_URL from app settings, overriding alembic.ini."""
    import sys
    import os
    # Ensure orchestration package is importable when running alembic CLI
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from orchestration.api.config import get_settings
    return get_settings().database.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without DB connection)."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Inner function executed inside async connect — runs the actual migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations inside a connection context."""
    url = get_database_url()
    connectable = create_async_engine(url, echo=False)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connected to the database)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
