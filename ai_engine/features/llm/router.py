"""LLM Provider Router — single entry point for all LLM calls."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from ai_engine.core.exceptions import (
    ProviderError,
    ProviderRateLimitError,
    SchemaValidationError,
)
from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.logging_.metrics import metrics
from ai_engine.core.types import ProviderType
from ai_engine.features.llm.base import LLMProvider, LLMResult

logger = get_logger(__name__)

# Exponential backoff base delay in seconds
_BACKOFF_BASE = 2.0
_BACKOFF_MAX = 30.0


def _build_provider(provider_type: ProviderType, settings: Any) -> LLMProvider:
    """Instantiate a provider from its type and settings.

    Args:
        provider_type: Which provider to build.
        settings: LLMSettings instance.

    Returns:
        Configured LLMProvider instance.

    Raises:
        ProviderError: If the provider cannot be instantiated.
    """
    from ai_engine.features.llm.providers.anthropic_provider import (
        AnthropicProvider,
    )  # noqa: PLC0415
    from ai_engine.features.llm.providers.deepseek_provider import DeepSeekProvider  # noqa: PLC0415
    from ai_engine.features.llm.providers.gemini_provider import GeminiProvider  # noqa: PLC0415
    from ai_engine.features.llm.providers.grok_provider import GrokProvider  # noqa: PLC0415
    from ai_engine.features.llm.providers.openai_provider import OpenAIProvider  # noqa: PLC0415
    from ai_engine.features.llm.providers.openrouter_provider import (
        OpenRouterProvider,
    )  # noqa: PLC0415

    mapping = {
        ProviderType.ANTHROPIC: lambda: AnthropicProvider(settings.anthropic_api_key),
        ProviderType.OPENAI: lambda: OpenAIProvider(settings.openai_api_key),
        ProviderType.GEMINI: lambda: GeminiProvider(settings.gemini_api_key),
        ProviderType.DEEPSEEK: lambda: DeepSeekProvider(settings.deepseek_api_key),
        ProviderType.GROK: lambda: GrokProvider(settings.grok_api_key),
        ProviderType.OPENROUTER: lambda: OpenRouterProvider(
            settings.openrouter_api_key, settings.openrouter_model
        ),
    }
    factory = mapping.get(provider_type)
    if factory is None:
        raise ProviderError(f"Unknown provider type: {provider_type}")
    return factory()


class LLMRouter:
    """Routes LLM calls through a provider chain with fallback and backoff.

    Providers are tried in order: primary first, then fallbacks.
    Rate-limit errors trigger exponential backoff before moving to the next provider.
    All other recoverable errors move immediately to the next provider.

    Args:
        settings: LLMSettings instance with provider config.
    """

    def __init__(self, settings: Any) -> None:
        self._settings = settings
        self._provider_chain: list[ProviderType] = [
            settings.primary_provider,
            *settings.fallback_providers,
        ]

    async def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        prompt_version: str = "",
    ) -> LLMResult:
        """Execute an LLM call through the provider chain.

        Args:
            prompt: Fully-rendered prompt string.
            output_schema: JSON Schema for response validation.
            prompt_version: Version tag of the prompt (for metadata).

        Returns:
            LLMResult from the first successful provider.

        Raises:
            ProviderError: When all providers in the chain fail.
            SchemaValidationError: When response fails schema validation.
        """
        last_error: Exception | None = None

        for idx, provider_type in enumerate(self._provider_chain):
            provider = _build_provider(provider_type, self._settings)
            logger.info(
                "llm_router.attempting",
                provider=provider.provider_name,
                chain_position=idx,
                prompt_version=prompt_version,
            )

            try:
                start = time.monotonic()
                result = await provider.complete(
                    prompt=prompt,
                    output_schema=output_schema,
                    max_retries=self._settings.max_retries,
                )
                result.prompt_version = prompt_version
                elapsed = time.monotonic() - start

                metrics.increment(f"llm.calls.{provider.provider_name}")
                metrics.record_latency(f"llm.latency.{provider.provider_name}", elapsed)

                logger.info(
                    "llm_router.success",
                    provider=provider.provider_name,
                    prompt_tokens=result.prompt_tokens,
                    completion_tokens=result.completion_tokens,
                    latency_seconds=round(elapsed, 3),
                )
                return result

            except ProviderRateLimitError as exc:
                last_error = exc
                backoff = min(_BACKOFF_BASE**idx, _BACKOFF_MAX)
                logger.warning(
                    "llm_router.rate_limit",
                    provider=provider.provider_name,
                    backoff_seconds=backoff,
                )
                metrics.increment(f"llm.rate_limit.{provider.provider_name}")
                await asyncio.sleep(backoff)

            except SchemaValidationError:
                raise  # Schema errors are not provider-specific; propagate immediately

            except ProviderError as exc:
                last_error = exc
                logger.warning(
                    "llm_router.provider_failed",
                    provider=provider.provider_name,
                    error=str(exc),
                    next_provider=(
                        self._provider_chain[idx + 1].value
                        if idx + 1 < len(self._provider_chain)
                        else None
                    ),
                )
                metrics.increment(f"llm.errors.{provider.provider_name}")

        raise ProviderError(
            f"All providers failed. Last error: {last_error}",
            context={"chain": [p.value for p in self._provider_chain]},
        )
