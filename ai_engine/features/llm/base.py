"""Abstract LLM provider interface and result types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResult:
    """Structured result from an LLM call.

    Attributes:
        content: Parsed response content (dict if JSON schema requested).
        provider: Provider name that served the request.
        model: Model identifier used.
        prompt_tokens: Input token count (0 if unavailable).
        completion_tokens: Output token count (0 if unavailable).
        latency_seconds: Wall-clock time for the call.
        prompt_version: Version tag of the prompt used.
    """

    content: Any
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_seconds: float = 0.0
    prompt_version: str = ""
    metadata: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base class for all LLM providers.

    Every provider must implement ``complete``. Providers handle their own
    SDK initialisation, error translation, and fallback signalling.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Default model identifier for this provider."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        max_retries: int = 3,
    ) -> LLMResult:
        """Send a prompt and return a validated structured response.

        Args:
            prompt: Fully-rendered prompt string.
            output_schema: JSON Schema dict describing the expected response shape.
            max_retries: Number of retry attempts on recoverable errors.

        Returns:
            LLMResult with parsed content and metadata.

        Raises:
            ProviderRateLimitError: On rate limit responses.
            ProviderQuotaError: On quota exhaustion.
            ProviderAuthError: On authentication failure.
            SchemaValidationError: When response does not match output_schema.
            ProviderError: On any other provider-level failure.
        """

    async def count_tokens(self, text: str) -> int:
        """Estimate token count for the given text (optional, stub by default).

        Args:
            text: Input text to count.

        Returns:
            Estimated token count, or 0 if not supported.
        """
        return 0
