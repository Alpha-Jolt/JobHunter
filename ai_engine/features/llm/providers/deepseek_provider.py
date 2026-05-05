"""DeepSeek provider — uses OpenAI SDK with DeepSeek base URL."""

from __future__ import annotations

import json
import time
from typing import Any

from ai_engine.core.exceptions import (
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    SchemaValidationError,
)
from ai_engine.features.llm.base import LLMProvider, LLMResult

_MODEL = "deepseek-chat"
_BASE_URL = "https://api.deepseek.com"


class DeepSeekProvider(LLMProvider):
    """LLM provider backed by DeepSeek via OpenAI-compatible API.

    Args:
        api_key: DeepSeek API key.
    """

    def __init__(self, api_key: str) -> None:
        try:
            from openai import AsyncOpenAI  # noqa: PLC0415

            self._client = AsyncOpenAI(api_key=api_key, base_url=_BASE_URL)
        except ImportError as exc:
            raise ProviderError(
                "openai package not installed. Run: pip install openai",
                provider=self.provider_name,
            ) from exc

    @property
    def provider_name(self) -> str:
        return "deepseek"

    @property
    def model_name(self) -> str:
        return _MODEL

    async def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        max_retries: int = 3,
    ) -> LLMResult:
        """Send prompt to DeepSeek and return structured JSON response."""
        from openai import APIStatusError  # noqa: PLC0415

        schema_instruction = (
            f"\n\nRespond with JSON matching this schema:\n{json.dumps(output_schema, indent=2)}"
        )
        start = time.monotonic()

        for attempt in range(max_retries):
            try:
                response = await self._client.chat.completions.create(
                    model=_MODEL,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "Respond ONLY with valid JSON."},
                        {"role": "user", "content": prompt + schema_instruction},
                    ],
                )
                elapsed = time.monotonic() - start
                raw_text = response.choices[0].message.content or ""

                try:
                    parsed = json.loads(raw_text)
                except json.JSONDecodeError as exc:
                    raise SchemaValidationError(
                        f"Response is not valid JSON: {raw_text[:200]}",
                        context={"attempt": attempt},
                    ) from exc

                usage = response.usage
                return LLMResult(
                    content=parsed,
                    provider=self.provider_name,
                    model=_MODEL,
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                    latency_seconds=elapsed,
                )

            except APIStatusError as exc:
                if exc.status_code == 429:
                    if attempt == max_retries - 1:
                        raise ProviderRateLimitError(self.provider_name) from exc
                elif exc.status_code == 401:
                    raise ProviderAuthError(self.provider_name) from exc
                else:
                    if attempt == max_retries - 1:
                        raise ProviderError(str(exc), provider=self.provider_name) from exc
            except SchemaValidationError:
                raise

        raise ProviderError("Max retries exceeded", provider=self.provider_name)
