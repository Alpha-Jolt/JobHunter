"""Unit tests for core configuration."""

from __future__ import annotations

from ai_engine.core.config import Settings


def test_settings_loads_defaults():
    """Settings instantiates with default values when no .env is present."""
    settings = Settings()
    assert settings.app_name == "JobHunter-AIEngine"
    assert settings.environment == "development"


def test_llm_settings_default_provider():
    """Default primary provider is Anthropic."""
    from ai_engine.core.types import ProviderType

    settings = Settings()
    assert settings.llm.primary_provider == ProviderType.ANTHROPIC


def test_variant_settings_defaults():
    """Variant budget matches configured .env values."""
    settings = Settings()
    assert settings.variants.max_variants_total == 15
    assert settings.variants.max_variants_per_session == 5
