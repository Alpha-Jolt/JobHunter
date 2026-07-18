"""Pydantic Settings configuration for JobHunter orchestration service."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_DATABASE_URL = (
    "postgresql+asyncpg://jobhunter:jobhunter@postgres:5432/jobhunter"
)


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(default=_DEFAULT_DATABASE_URL, alias="DATABASE_URL")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    use_alembic_migrations: bool = Field(
        default=False,
        alias="USE_ALEMBIC_MIGRATIONS",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def _empty_db_url(cls, v: object) -> object:
        # Empty GitHub secret must not become None
        if v is None or (isinstance(v, str) and not v.strip()):
            return _DEFAULT_DATABASE_URL
        return v


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    secret_key_approval: str = Field(
        default="changeme-32-char-secret-key-here!", alias="SECRET_KEY_APPROVAL"
    )
    approval_token_secret: str = Field(
        default="changeme-32-char-secret-key-here!", alias="APPROVAL_TOKEN_SECRET"
    )
    max_applications_per_day: int = Field(default=10, alias="MAX_APPLICATIONS_PER_DAY")
    max_variants_per_session: int = Field(default=15, alias="MAX_VARIANTS_PER_SESSION")
    max_variants_total: int = Field(default=50, alias="MAX_VARIANTS_TOTAL")
    internal_api_key: str = Field(
        default="dev-internal-api-key-change-me-32ch", alias="INTERNAL_API_KEY"
    )

    @field_validator(
        "approval_token_secret",
        "secret_key_approval",
        "internal_api_key",
        mode="before",
    )
    @classmethod
    def _empty_str_to_default(cls, v: object, info) -> object:
        if v is None or (isinstance(v, str) and not v.strip()):
            defaults = {
                "approval_token_secret": "changeme-32-char-secret-key-here!",
                "secret_key_approval": "changeme-32-char-secret-key-here!",
                "internal_api_key": "dev-internal-api-key-change-me-32ch",
            }
            return defaults.get(info.field_name, v)
        return v

    @model_validator(mode="after")
    def _ensure_approval_secrets(self) -> "APIConfig":
        if len(self.approval_token_secret) < 32:
            if len(self.secret_key_approval) >= 32:
                object.__setattr__(
                    self, "approval_token_secret", self.secret_key_approval
                )
            else:
                raise ValueError(
                    "APPROVAL_TOKEN_SECRET (or SECRET_KEY_APPROVAL) must be at least 32 characters"
                )
        if len(self.secret_key_approval) < 32:
            raise ValueError("SECRET_KEY_APPROVAL must be at least 32 characters")
        if len(self.internal_api_key) < 16:
            raise ValueError("INTERNAL_API_KEY must be at least 16 characters")
        return self


class ServicePaths(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    scraper_output_dir: str = Field(default="./output/final", alias="SCRAPER_OUTPUT_DIR")
    ai_resume_dir: str = Field(default="./resumes/", alias="AI_RESUME_DIR")
    registry_path: str = Field(default="./registries/jobs.json", alias="REGISTRY_PATH")


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_primary_provider: str = Field(default="openrouter", alias="LLM_PRIMARY_PROVIDER")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")


class MailConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    sendgrid_api_key: Optional[str] = Field(default=None, alias="SENDGRID_API_KEY")
    mail_sender_email: str = Field(default="apply@myjobhunter.in", alias="MAIL_SENDER_EMAIL")
    mail_bridge_url: str = Field(default="http://localhost:3009", alias="MAIL_BRIDGE_URL")
    mail_bridge_api_key: str = Field(default="", alias="MAIL_BRIDGE_API_KEY")
    mailbridge_webhook_secret: str = Field(default="", alias="MAILBRIDGE_WEBHOOK_SECRET")
    mailbridge_webhook_id: Optional[str] = Field(default=None, alias="MAILBRIDGE_WEBHOOK_ID")


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str = Field(
        default="changeme-jwt-secret-key-minimum-32chars!", alias="JWT_SECRET"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiry_minutes: int = Field(default=15, alias="JWT_EXPIRY_MINUTES")
    refresh_token_expiry_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRY_DAYS")
    min_password_length: int = Field(default=8, alias="MIN_PASSWORD_LENGTH")
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    cookie_domain: str = Field(default="", alias="COOKIE_DOMAIN")

    @field_validator("jwt_secret", mode="before")
    @classmethod
    def _empty_jwt_to_default(cls, v: object) -> object:
        if v is None or (isinstance(v, str) and not v.strip()):
            return "changeme-jwt-secret-key-minimum-32chars!"
        return v

    @field_validator("jwt_secret")
    @classmethod
    def _validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v


class MinIOConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    minio_endpoint: str = Field(default="minio:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="jobhunter-resumes", alias="MINIO_BUCKET_NAME")
    minio_avatar_bucket: str = Field(
        default="jobhunter-avatars", alias="MINIO_AVATAR_BUCKET_NAME"
    )
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")
    minio_external_endpoint: str | None = Field(
        default=None, alias="MINIO_EXTERNAL_ENDPOINT"
    )
    minio_external_secure: bool | None = Field(
        default=None, alias="MINIO_EXTERNAL_SECURE"
    )


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")


class OtelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    otel_exporter_otlp_endpoint: Optional[str] = Field(
        default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    otel_service_name: str = Field(
        default="jobhunter-orchestration", alias="OTEL_SERVICE_NAME"
    )


class Settings(BaseSettings):
    """Aggregated application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    paths: ServicePaths = Field(default_factory=ServicePaths)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mail: MailConfig = Field(default_factory=MailConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    minio: MinIOConfig = Field(default_factory=MinIOConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    otel: OtelConfig = Field(default_factory=OtelConfig)

    @field_validator("database", mode="before")
    @classmethod
    def _build_database(cls, v):
        if isinstance(v, dict):
            return DatabaseConfig(**v)
        return v or DatabaseConfig()

    @field_validator("api", mode="before")
    @classmethod
    def _build_api(cls, v):
        if isinstance(v, dict):
            return APIConfig(**v)
        return v or APIConfig()

    @field_validator("paths", mode="before")
    @classmethod
    def _build_paths(cls, v):
        if isinstance(v, dict):
            return ServicePaths(**v)
        return v or ServicePaths()

    @field_validator("llm", mode="before")
    @classmethod
    def _build_llm(cls, v):
        if isinstance(v, dict):
            return LLMConfig(**v)
        return v or LLMConfig()

    @field_validator("mail", mode="before")
    @classmethod
    def _build_mail(cls, v):
        if isinstance(v, dict):
            return MailConfig(**v)
        return v or MailConfig()

    @field_validator("redis", mode="before")
    @classmethod
    def _build_redis(cls, v):
        if isinstance(v, dict):
            return RedisConfig(**v)
        return v or RedisConfig()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
