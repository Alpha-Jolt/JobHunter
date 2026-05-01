"""AI Engine configuration — all settings loaded from environment."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_engine.core.types import ProviderType


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="LLM_", extra="ignore")

    primary_provider: ProviderType = ProviderType.ANTHROPIC
    fallback_providers: list[ProviderType] = [
        ProviderType.OPENAI,
        ProviderType.GEMINI,
    ]
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=60, ge=5, le=300)

    # Provider API keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    grok_api_key: str = Field(default="", alias="GROK_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openai/gpt-4o-mini", alias="OPENROUTER_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


class PathSettings(BaseSettings):
    """File path configuration."""

    model_config = SettingsConfigDict(env_prefix="PATH_", extra="ignore")

    scraper_output_dir: Path = Path("output/final")
    ai_output_dir: Path = Path("ai_output")
    prompts_dir: Path = Path("ai_engine/features/llm/prompting/prompts")
    variant_registry_path: Path = Path("ai_output/variant_registry.json")

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


class Settings(BaseSettings):
    """Root configuration object — single source of truth."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm: LLMSettings = Field(default_factory=LLMSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    variants: VariantSettings = Field(default_factory=VariantSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Application identity
    app_name: str = Field(default="JobHunter-AIEngine", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


def get_settings(env_file: str | Path = ".env") -> Settings:
    """Load and return application settings.

    Args:
        env_file: Path to the .env file.

    Returns:
        Populated Settings instance.
    """
    return Settings(_env_file=str(env_file))  # type: ignore[call-arg]
