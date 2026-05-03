"""Settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    api_port: int = 8003
    api_host: str = "0.0.0.0"
    api_env: str = "development"

    # Auth
    auth_enabled: bool = True
    api_key_token: str = "secret-phase-0"

    # Registries
    registry_jobs_path: str = "registries/jobs.json"
    registry_variants_path: str = "registries/variants.json"
    registry_applications_path: str = "registries/applications.json"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "jobhunter-resumes"
    minio_use_ssl: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    return Settings()
