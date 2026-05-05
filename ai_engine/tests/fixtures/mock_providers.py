"""Mock LLM providers for unit tests."""

from __future__ import annotations

from typing import Any

from ai_engine.features.llm.base import LLMProvider, LLMResult


class MockProvider(LLMProvider):
    """Mock LLM provider that returns a configurable response.

    Args:
        response_content: Dict to return as LLM response content.
        should_fail: If True, raises ProviderError on complete().
    """

    def __init__(self, response_content: dict, should_fail: bool = False) -> None:
        self._response = response_content
        self._should_fail = should_fail

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-model"

    async def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        max_retries: int = 3,
    ) -> LLMResult:
        if self._should_fail:
            from ai_engine.core.exceptions import ProviderError  # noqa: PLC0415

            raise ProviderError("Mock provider failure", provider="mock")
        return LLMResult(
            content=self._response,
            provider="mock",
            model="mock-model",
            prompt_tokens=50,
            completion_tokens=100,
            latency_seconds=0.1,
        )
