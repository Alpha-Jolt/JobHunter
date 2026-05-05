"""Integration test: provider fallback chain."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_engine.core.exceptions import ProviderRateLimitError
from ai_engine.core.types import ProviderType
from ai_engine.features.llm.base import LLMResult
from ai_engine.features.llm.router import LLMRouter


@pytest.mark.asyncio
async def test_provider_fallback_chain_uses_second_on_rate_limit():
    """When primary provider hits rate limit, fallback provider is used."""
    fallback_result = LLMResult(
        content={"from": "fallback"}, provider="openai", model="gpt-4o-mini"
    )
    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ProviderRateLimitError("anthropic")
        return fallback_result

    settings = MagicMock()
    settings.primary_provider = ProviderType.ANTHROPIC
    settings.fallback_providers = [ProviderType.OPENAI]
    settings.max_retries = 1
    settings.anthropic_api_key = "test"
    settings.openai_api_key = "test"
    settings.gemini_api_key = "test"
    settings.deepseek_api_key = "test"
    settings.grok_api_key = "test"
    settings.openrouter_api_key = "test"
    settings.openrouter_model = "openai/gpt-4o-mini"

    with patch("ai_engine.features.llm.router._build_provider") as mock_build:
        mock_provider = MagicMock()
        mock_provider.provider_name = "mock"
        mock_provider.complete = AsyncMock(side_effect=side_effect)
        mock_build.return_value = mock_provider

        router = LLMRouter(settings)
        result = await router.complete("test", {})

    assert result.content == {"from": "fallback"}
    assert call_count == 2
