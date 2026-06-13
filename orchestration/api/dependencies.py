"""FastAPI dependency injection helpers."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.config import Settings, get_settings
from orchestration.db.connection import get_session_factory
from orchestration.repositories.postgres_job_repository import PostgresJobRepository
from orchestration.repositories.postgres_variant_repository import (
    PostgresVariantRepository,
)
from orchestration.repositories.postgres_application_repository import (
    PostgresApplicationRepository,
)
from orchestration.services.mail_service import MailService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for use in route handlers."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_app_settings(settings: Settings = Depends(get_settings)) -> Settings:
    return settings


async def get_job_registry(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresJobRepository:
    return PostgresJobRepository(session)


async def get_variant_registry(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresVariantRepository:
    return PostgresVariantRepository(session)


async def get_application_log(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresApplicationRepository:
    return PostgresApplicationRepository(session)


async def get_scraper_runs_repo(session: AsyncSession = Depends(get_db_session)):
    from orchestration.repositories.postgres_scraper_runs_repository import (
        PostgresScraperRunsRepository,
    )
    return PostgresScraperRunsRepository(session)


async def get_mail_service(
    settings: Settings = Depends(get_settings),
    job_registry: PostgresJobRepository = Depends(get_job_registry),
    variant_registry: PostgresVariantRepository = Depends(get_variant_registry),
    application_log: PostgresApplicationRepository = Depends(get_application_log),
) -> MailService:
    import boto3
    scheme = "https" if settings.minio.minio_secure else "http"
    s3_client = boto3.client(
        "s3",
        endpoint_url=f"{scheme}://{settings.minio.minio_endpoint}",
        aws_access_key_id=settings.minio.minio_access_key,
        aws_secret_access_key=settings.minio.minio_secret_key,
        region_name="us-east-1",  # required by boto3, ignored by MinIO
    )
    return MailService(
        mail_bridge_url=settings.mail.mail_bridge_url,
        mail_bridge_api_key=settings.mail.mail_bridge_api_key,
        job_registry=job_registry,
        variant_registry=variant_registry,
        application_log=application_log,
        s3_client=s3_client,
        max_applications_per_day=settings.api.max_applications_per_day,
    )

# ── Auth dependencies (re-exported from auth module) ─────────────────────────
from orchestration.auth.dependencies import get_current_user, require_role  # noqa: F401, E402
