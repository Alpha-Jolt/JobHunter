"""FastAPI dependency injection helpers."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from functools import lru_cache
import boto3

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


@lru_cache(maxsize=2)
def _get_cached_s3_client(endpoint_url: str, access_key: str, secret_key: str):
    from boto3.session import Config
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"})
    )


def get_internal_s3_client(settings: Settings = Depends(get_settings)):
    scheme = "https" if settings.minio.minio_secure else "http"
    endpoint_url = f"{scheme}://{settings.minio.minio_endpoint}"
    return _get_cached_s3_client(endpoint_url, settings.minio.minio_access_key, settings.minio.minio_secret_key)


def get_external_s3_client(settings: Settings = Depends(get_settings)):
    if settings.minio.minio_external_endpoint:
        endpoint = settings.minio.minio_external_endpoint
        secure = settings.minio.minio_external_secure if settings.minio.minio_external_secure is not None else settings.minio.minio_secure
        scheme = "https" if secure else "http"
    else:
        scheme = "https" if settings.minio.minio_secure else "http"
        endpoint = settings.minio.minio_endpoint
        if endpoint.startswith("minio:"):
            endpoint = endpoint.replace("minio:", "localhost:")
            
    endpoint_url = f"{scheme}://{endpoint}"
    return _get_cached_s3_client(endpoint_url, settings.minio.minio_access_key, settings.minio.minio_secret_key)


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


async def get_profile_repo(session: AsyncSession = Depends(get_db_session)):
    from orchestration.repositories.postgres_profile_repository import (
        PostgresProfileRepository,
    )
    return PostgresProfileRepository(session)


async def get_mail_service(
    settings: Settings = Depends(get_settings),
    job_registry: PostgresJobRepository = Depends(get_job_registry),
    variant_registry: PostgresVariantRepository = Depends(get_variant_registry),
    application_log: PostgresApplicationRepository = Depends(get_application_log),
) -> MailService:
    s3_client = get_internal_s3_client(settings)
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
