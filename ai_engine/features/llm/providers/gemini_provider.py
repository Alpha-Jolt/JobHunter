"""Google Gemini provider implementation."""

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

_MODEL = "gemini-2.0-flash"


class GeminiProvider(LLMProvider):
    """LLM provider backed by Google Gemini.

    Args:
        api_key: Google AI API key.
    """

    def __init__(self, api_key: str) -> None:
        try:
            import google.generativeai as genai  # noqa: PLC0415

            genai.configure(api_key=api_key)
            self._genai = genai
        except ImportError as exc:
            raise ProviderError(
                "google-generativeai package not installed. Run: pip install google-generativeai",
                provider=self.provider_name,
            ) from exc

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return _MODEL

    async def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        max_retries: int = 3,
    ) -> LLMResult:
        """Send prompt to Gemini and return structured JSON response."""
        import asyncio  # noqa: PLC0415

        schema_instruction = (
            "\n\nRespond ONLY with valid JSON matching this schema:\n"
            + json.dumps(output_schema, indent=2)
        )
        full_prompt = prompt + schema_instruction
        start = time.monotonic()

        for attempt in range(max_retries):
            try:
                model = self._genai.GenerativeModel(
                    model_name=_MODEL,
                    generation_config={"response_mime_type": "application/json"},
                )
                # Gemini SDK is sync; run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(full_prompt),
                )
                elapsed = time.monotonic() - start
                raw_text = response.text.strip()

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
                    latency_seconds=elapsed,
                )

            except SchemaValidationError:
                raise
            except Exception as exc:
                err_str = str(exc).lower()
                if "rate" in err_str or "429" in err_str:
                    if attempt == max_retries - 1:
                        raise ProviderRateLimitError(self.provider_name) from exc
                elif "auth" in err_str or "api key" in err_str:
                    raise ProviderAuthError(self.provider_name) from exc
                else:
                    if attempt == max_retries - 1:
                        raise ProviderError(str(exc), provider=self.provider_name) from exc

        raise ProviderError("Max retries exceeded", provider=self.provider_name)
