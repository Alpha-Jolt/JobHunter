"""AI Engine configuration — all settings loaded from environment."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Self

from ai_engine.core.types import ProviderType


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="LLM_", extra="ignore")

    primary_provider: ProviderType = ProviderType.OPENROUTER
    fallback_providers: list[ProviderType] = [
        ProviderType.DEEPSEEK,
        ProviderType.ANTHROPIC,
        ProviderType.OPENAI,
        ProviderType.GEMINI,
        ProviderType.GROK,
    ]
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=60, ge=5, le=300)

    # Provider API keys
    anthropic_api_key: SecretStr = Field(default=SecretStr(""), alias="ANTHROPIC_API_KEY")
    openai_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENAI_API_KEY")
    gemini_api_key: SecretStr = Field(default=SecretStr(""), alias="GEMINI_API_KEY")
    deepseek_api_key: SecretStr = Field(default=SecretStr(""), alias="DEEPSEEK_API_KEY")
    grok_api_key: SecretStr = Field(default=SecretStr(""), alias="GROK_API_KEY")
    openrouter_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openai/gpt-4o-mini", alias="OPENROUTER_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


class PathSettings(BaseSettings):
    """File path configuration."""

    model_config = SettingsConfigDict(env_prefix="PATH_", extra="ignore")

    scraper_output_dir: Path = Path("output/final")
    ai_output_dir: Path = Path("ai_output")
    prompts_dir: Path = Path("ai_engine/features/llm/prompting/prompts")
    variant_registry_path: Path = Path("ai_output/variant_registry.json")
    use_shared_registry: bool = Field(default=False, alias="USE_SHARED_REGISTRY")
    shared_jobs_registry_path: str = Field(
        default="registries/jobs.json", alias="SHARED_JOBS_REGISTRY_PATH"
    )
    shared_variants_registry_path: str = Field(
        default="registries/variants.json", alias="SHARED_VARIANTS_REGISTRY_PATH"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


class VariantSettings(BaseSettings):
    """Variant budget and management configuration."""

    model_config = SettingsConfigDict(env_prefix="VARIANT_", extra="ignore")

    max_variants_total: int = Field(default=50, ge=1, alias="MAX_VARIANTS_TOTAL")
    max_variants_per_session: int = Field(default=10, ge=1, alias="MAX_VARIANTS_PER_SESSION")
    budget_warning_threshold: float = Field(default=0.8, ge=0.0, le=1.0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore")

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    format: str = Field(default="json", alias="LOG_FORMAT")  # json | text

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"Log level must be one of {valid}")
        return v.upper()


class MinIOSettings(BaseSettings):
    """MinIO S3 configuration."""

    model_config = SettingsConfigDict(env_prefix="MINIO_", env_file=".env", extra="ignore")

    endpoint: str = Field(default="localhost:9000")
    access_key: SecretStr = Field(default=SecretStr(""))
    secret_key: SecretStr = Field(default=SecretStr(""))
    bucket_name: str = Field(default="jobhunter-resumes")
    use_ssl: bool = Field(default=True)
    enabled: bool = Field(default=True)


class ApprovalSettings(BaseSettings):
    """Approval token HMAC key ring configuration."""

    model_config = SettingsConfigDict(
        env_prefix="APPROVAL_", env_file=".env", extra="ignore"
    )

    # JSON string: {"k1": "secret1", "k2": "secret2"}
    keys_json: SecretStr = Field(alias="APPROVAL_KEYS")
    active_key_id: str = Field(alias="APPROVAL_ACTIVE_KEY")

    @property
    def keyring(self) -> dict[str, str]:
        """Parse keys_json into {key_id: raw_secret} dict."""
        import json
        raw = json.loads(self.keys_json.get_secret_value())
        if not isinstance(raw, dict) or not raw:
            raise ValueError("APPROVAL_KEYS must be a non-empty JSON object.")
        if self.active_key_id not in raw:
            raise ValueError(
                f"APPROVAL_ACTIVE_KEY '{self.active_key_id}' not found in APPROVAL_KEYS."
            )
        return raw


class Settings(BaseSettings):
    """Root configuration object — single source of truth."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm: LLMSettings = Field(default_factory=LLMSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    variants: VariantSettings = Field(default_factory=VariantSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    approval: ApprovalSettings = Field(default_factory=ApprovalSettings)

    # Application identity
    app_name: str = Field(default="JobHunter-AIEngine", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    orchestration_api_url: str = Field(
        default="https://jobhunter-api:8000", alias="INTERNAL_API_URL"
    )

    @model_validator(mode="after")
    def _enforce_https_on_production(self) -> Self:
        """Refuse to start if HTTP is used outside a development environment."""
        is_dev = self.environment.lower() in {"development", "local", "dev"}
        url_is_http = self.orchestration_api_url.startswith("http://")
        minio_no_ssl = self.minio.enabled and not self.minio.use_ssl

        if not is_dev and (url_is_http or minio_no_ssl):
            problems = []
            if url_is_http:
                problems.append(f"orchestration_api_url uses HTTP: {self.orchestration_api_url}")
            if minio_no_ssl:
                problems.append("MinIO use_ssl=False on non-development environment")
            raise ValueError(
                "Insecure HTTP configuration detected on non-development environment. "
                f"Problems: {'; '.join(problems)}. "
                "Set ENVIRONMENT=development to override, or fix your URLs."
            )
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


def get_settings(env_file: str | Path = ".env") -> Settings:
    """Load and return application settings.

    Args:
        env_file: Path to the .env file.

    Returns:
        Populated Settings instance.
    """
    return Settings(_env_file=str(env_file))  # type: ignore[call-arg]
