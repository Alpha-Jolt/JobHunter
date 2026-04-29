"""Configuration management for JobHunter Scraper Engine."""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Scraper ---
    headless: bool = True
    browser_pool_size: int = Field(default=3, ge=1, le=10)
    scraper_timeout_ms: int = Field(default=30_000, ge=1_000)
    debug_screenshots: bool = False
    dev_mode: bool = True
    pages_per_search: int = Field(default=5, ge=1, le=50)

    # --- Rate Limiting (requests per second) ---
    indeed_rate_limit: float = Field(default=1.0, gt=0)
    naukri_rate_limit: float = Field(default=0.5, gt=0)

    # --- Proxy ---
    proxy_list: str = ""  # comma-separated proxy URLs
    proxy_strategy: str = "round_robin"
    proxy_fallback_to_direct: bool = True

    # --- Retry ---
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_base_delay: float = Field(default=2.0, gt=0)
    retry_max_delay: float = Field(default=60.0, gt=0)

    # --- Logging ---
    log_level: str = "INFO"
    log_format: str = "json"
    log_dir: Path = Path("logs")

    # --- Sentry ---
    sentry_dsn: Optional[str] = None

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Output ---
    output_dir: Path = Path("output")
    output_formats: str = "json,csv"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper

    @field_validator("proxy_strategy")
    @classmethod
    def validate_proxy_strategy(cls, v: str) -> str:
        allowed = {"round_robin", "random", "weighted"}
        if v not in allowed:
            raise ValueError(f"proxy_strategy must be one of {allowed}")
        return v

    def get_proxy_list(self) -> List[str]:
        """Return parsed proxy list."""
        if not self.proxy_list:
            return []
        return [p.strip() for p in self.proxy_list.split(",") if p.strip()]

    def get_output_formats(self) -> List[str]:
        """Return parsed output format list."""
        return [f.strip() for f in self.output_formats.split(",") if f.strip()]


# Module-level singleton — import this everywhere
config = Config()
