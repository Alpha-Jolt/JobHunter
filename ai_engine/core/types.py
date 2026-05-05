"""Shared type definitions, enums, and constants for the AI Engine."""

from enum import Enum


class ProviderType(str, Enum):
    """Supported LLM provider types."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROK = "grok"
    OPENROUTER = "openrouter"


class ResumeFormat(str, Enum):
    """Supported resume file formats."""

    PDF = "pdf"
    DOCX = "docx"


class ApprovalStatus(str, Enum):
    """Variant approval states."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PipelineMode(str, Enum):
    """Pipeline execution modes."""

    GENERATE = "generate"
    RELEASE = "release"


class ErrorCategory(str, Enum):
    """Error categories for observability."""

    CONFIG_ERROR = "config_error"
    PROVIDER_ERROR = "provider_error"
    VALIDATION_ERROR = "validation_error"
    FABRICATION_ERROR = "fabrication_error"
    LOGIC_ERROR = "logic_error"
    IO_ERROR = "io_error"


class ApprovalMethod(str, Enum):
    """Methods by which a variant can be approved."""

    EMAIL_TOKEN = "email_token"
    IN_APP = "in_app"
    CLI = "cli"


# File naming conventions
VARIANT_REGISTRY_FILENAME = "variant_registry.json"
AI_OUTPUT_DIR = "ai_output"
SCRAPER_OUTPUT_DIR = "output/final"

# Variant budget defaults (overridden by config)
DEFAULT_MAX_VARIANTS_TOTAL = 50
DEFAULT_MAX_VARIANTS_PER_SESSION = 10

# LLM defaults
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 60
APPROVAL_TOKEN_TTL_HOURS = 24
