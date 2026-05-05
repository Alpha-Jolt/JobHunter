"""Unit tests for the LLM router."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_engine.core.exceptions import ProviderError, ProviderRateLimitError
from ai_engine.core.types import ProviderType
from ai_engine.features.llm.base import LLMResult
from ai_engine.features.llm.router import LLMRouter


def _make_settings(primary: ProviderType = ProviderType.ANTHROPIC, fallbacks: list | None = None):
    settings = MagicMock()
    settings.primary_provider = primary
    settings.fallback_providers = fallbacks or [ProviderType.OPENAI]
    settings.max_retries = 1
    settings.anthropic_api_key = "test"
    settings.openai_api_key = "test"
    settings.gemini_api_key = "test"
    settings.deepseek_api_key = "test"
    settings.grok_api_key = "test"
    settings.openrouter_api_key = "test"
    settings.openrouter_model = "openai/gpt-4o-mini"
    return settings


@pytest.mark.asyncio
async def test_router_returns_result_on_success():
    """Router returns LLMResult when primary provider succeeds."""
    expected = LLMResult(content={"key": "value"}, provider="mock", model="mock")
    settings = _make_settings()

    with patch("ai_engine.features.llm.router._build_provider") as mock_build:
        mock_provider = MagicMock()
        mock_provider.provider_name = "mock"
        mock_provider.complete = AsyncMock(return_value=expected)
        mock_build.return_value = mock_provider

        router = LLMRouter(settings)
        result = await router.complete("test prompt", {})

    assert result.content == {"key": "value"}


@pytest.mark.asyncio
async def test_router_falls_back_on_rate_limit():
    """Router moves to fallback provider when primary hits rate limit."""
    fallback_result = LLMResult(content={"fallback": True}, provider="openai", model="gpt-4o-mini")
    settings = _make_settings()
    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ProviderRateLimitError("anthropic")
        return fallback_result

    with patch("ai_engine.features.llm.router._build_provider") as mock_build:
        mock_provider = MagicMock()
        mock_provider.provider_name = "mock"
        mock_provider.complete = AsyncMock(side_effect=side_effect)
        mock_build.return_value = mock_provider

        router = LLMRouter(settings)
        result = await router.complete("test prompt", {})

    assert result.content == {"fallback": True}


@pytest.mark.asyncio
async def test_router_raises_when_all_providers_fail():
    """Router raises ProviderError when all providers in chain fail."""
    settings = _make_settings(fallbacks=[])

    with patch("ai_engine.features.llm.router._build_provider") as mock_build:
        mock_provider = MagicMock()
        mock_provider.provider_name = "mock"
        mock_provider.complete = AsyncMock(side_effect=ProviderError("fail", provider="mock"))
        mock_build.return_value = mock_provider

        router = LLMRouter(settings)
        with pytest.raises(ProviderError):
            await router.complete("test prompt", {})
