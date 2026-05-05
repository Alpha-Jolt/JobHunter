"""Custom exception hierarchy for the AI Engine."""


class AIEngineError(Exception):
    """Base exception for all AI Engine errors."""

    def __init__(self, message: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ConfigError(AIEngineError):
    """Raised when configuration is missing or invalid."""


class ProviderError(AIEngineError):
    """Raised when an LLM provider call fails."""

    def __init__(
        self,
        message: str,
        provider: str = "",
        category: str = "unknown",
        context: dict | None = None,
    ) -> None:
        super().__init__(message, context)
        self.provider = provider
        self.category = category  # rate_limit | quota | auth | schema_error | model_error


class ProviderRateLimitError(ProviderError):
    """Raised when a provider returns a rate limit response."""

    def __init__(self, provider: str, context: dict | None = None) -> None:
        super().__init__(
            f"Rate limit hit on {provider}",
            provider=provider,
            category="rate_limit",
            context=context,
        )


class ProviderQuotaError(ProviderError):
    """Raised when a provider quota is exhausted."""

    def __init__(self, provider: str, context: dict | None = None) -> None:
        super().__init__(
            f"Quota exhausted on {provider}", provider=provider, category="quota", context=context
        )


class ProviderAuthError(ProviderError):
    """Raised when a provider authentication fails."""

    def __init__(self, provider: str, context: dict | None = None) -> None:
        super().__init__(
            f"Auth failed on {provider}", provider=provider, category="auth", context=context
        )


class SchemaValidationError(AIEngineError):
    """Raised when LLM output fails schema validation."""

    def __init__(self, message: str, field: str = "", context: dict | None = None) -> None:
        super().__init__(message, context)
        self.field = field


class ValidationError(AIEngineError):
    """Raised when input data fails validation."""


class FabricationDetectedError(AIEngineError):
    """Raised when fabricated content is detected in LLM output."""

    def __init__(self, fabricated_fields: list[str], context: dict | None = None) -> None:
        super().__init__(f"Fabrication detected in fields: {fabricated_fields}", context)
        self.fabricated_fields = fabricated_fields


class VariantBudgetExceededError(AIEngineError):
    """Raised when the variant generation budget is exhausted."""


class ApprovalRequiredError(AIEngineError):
    """Raised when an unapproved variant is used in a release operation."""

    def __init__(self, variant_id: str, context: dict | None = None) -> None:
        super().__init__(f"Variant {variant_id} is not approved for release", context)
        self.variant_id = variant_id


class IngestionError(AIEngineError):
    """Raised when job record ingestion fails."""


class ResumeParsingError(AIEngineError):
    """Raised when resume parsing fails."""


class OutputRenderError(AIEngineError):
    """Raised when output file rendering fails."""


class PromptNotFoundError(AIEngineError):
    """Raised when a requested prompt file does not exist."""

    def __init__(self, prompt_name: str, context: dict | None = None) -> None:
        super().__init__(f"Prompt not found: {prompt_name}", context)
        self.prompt_name = prompt_name
