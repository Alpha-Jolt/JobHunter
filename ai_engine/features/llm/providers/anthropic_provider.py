"""Anthropic Claude provider implementation."""

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

_MODEL = "claude-sonnet-4-5"


class AnthropicProvider(LLMProvider):
    """LLM provider backed by Anthropic Claude.

    Args:
        api_key: Anthropic API key.
    """

    def __init__(self, api_key: str) -> None:
        try:
            import anthropic  # noqa: PLC0415

            self._client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError as exc:
            raise ProviderError(
                "anthropic package not installed. Run: pip install anthropic",
                provider=self.provider_name,
            ) from exc

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return _MODEL

    async def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        max_retries: int = 3,
    ) -> LLMResult:
        """Send prompt to Claude and return structured JSON response.

        Args:
            prompt: Fully-rendered prompt string.
            output_schema: JSON Schema for response validation.
            max_retries: Retry attempts on recoverable errors.

        Returns:
            LLMResult with parsed content.

        Raises:
            ProviderRateLimitError: On 429 responses.
            ProviderQuotaError: On quota exhaustion.
            ProviderAuthError: On auth failure.
            SchemaValidationError: When response JSON is invalid.
            ProviderError: On other failures.
        """
        import anthropic  # noqa: PLC0415

        system_msg = (
            "You are a precise JSON-only assistant. "
            "Respond ONLY with valid JSON matching the provided schema. "
            "No markdown, no explanation, no extra text."
        )
        schema_instruction = (
            f"\n\nRespond with JSON matching this schema:\n{json.dumps(output_schema, indent=2)}"
        )

        start = time.monotonic()
        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = await self._client.messages.create(
                    model=_MODEL,
                    max_tokens=4096,
                    system=system_msg,
                    messages=[{"role": "user", "content": prompt + schema_instruction}],
                )
                elapsed = time.monotonic() - start
                raw_text = response.content[0].text.strip()

                try:
                    parsed = json.loads(raw_text)
                except json.JSONDecodeError as exc:
                    raise SchemaValidationError(
                        f"Response is not valid JSON: {raw_text[:200]}",
                        context={"attempt": attempt},
                    ) from exc

                return LLMResult(
                    content=parsed,
                    provider=self.provider_name,
                    model=_MODEL,
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    latency_seconds=elapsed,
                )

            except anthropic.RateLimitError as exc:
                last_error = ProviderRateLimitError(self.provider_name)
                if attempt == max_retries - 1:
                    raise last_error from exc
            except anthropic.AuthenticationError as exc:
                raise ProviderAuthError(self.provider_name) from exc
            except anthropic.BadRequestError as exc:
                raise ProviderError(
                    str(exc), provider=self.provider_name, category="model_error"
                ) from exc
            except SchemaValidationError:
                raise
            except Exception as exc:
                last_error = ProviderError(str(exc), provider=self.provider_name)
                if attempt == max_retries - 1:
                    raise last_error from exc

        raise ProviderError("Max retries exceeded", provider=self.provider_name)
