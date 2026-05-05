"""Dependency injection — singleton registry and MinIO instances."""

import os
import sys

import structlog
from fastapi import FastAPI

logger = structlog.get_logger(__name__)

_job_registry = None
_variant_registry = None
_application_log = None
_minio_uploader = None


def _add_shared_to_path() -> None:
    try:
        import shared  # noqa: F401
    except ImportError:
        base = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.normpath(
            os.path.join(
                base, "..", "..", "..", "..",
                "package", "JobHunter-DPL", "JobHunter-DPL",
            )
        )
        if os.path.isdir(candidate) and candidate not in sys.path:
            sys.path.insert(0, candidate)


def setup_dependencies(app: FastAPI) -> None:
    @app.on_event("startup")
    async def startup():
        global _job_registry, _variant_registry, _application_log, _minio_uploader

        _add_shared_to_path()

        from shared.registries.job_registry import JobRegistry
        from shared.registries.variant_registry import VariantRegistry
        from shared.registries.application_log import ApplicationLog

        from config import get_settings
        settings = get_settings()

        _job_registry = JobRegistry(file_path=settings.registry_jobs_path)
        _variant_registry = VariantRegistry(file_path=settings.registry_variants_path)
        _application_log = ApplicationLog(file_path=settings.registry_applications_path)

        try:
            ai_engine_path = os.path.normpath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ai_engine")
            )
            if ai_engine_path not in sys.path:
                sys.path.insert(0, ai_engine_path)
            from features.output.storage.minio_uploader import MinIOUploader
            _minio_uploader = MinIOUploader(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                bucket_name=settings.minio_bucket_name,
                use_ssl=settings.minio_use_ssl,
            )
        except Exception as exc:
            logger.warning("minio_init_failed", error=str(exc))
            _minio_uploader = None

        logger.info("dependencies_initialized")


async def get_job_registry():
    assert _job_registry is not None, "JobRegistry not initialized"
    return _job_registry


async def get_variant_registry():
    assert _variant_registry is not None, "VariantRegistry not initialized"
    return _variant_registry


async def get_application_log():
    assert _application_log is not None, "ApplicationLog not initialized"
    return _application_log


async def get_minio_uploader():
    return _minio_uploader
