"""Error categorization and structured reporting."""

from __future__ import annotations

from ai_engine.core.logging_.logger import get_logger
from ai_engine.core.types import ErrorCategory

logger = get_logger(__name__)


def report_error(
    error: Exception,
    category: ErrorCategory,
    module: str,
    context: dict | None = None,
) -> None:
    """Log a structured error report at the boundary where it is caught.

    Args:
        error: The exception instance.
        category: Error category for filtering and alerting.
        module: Module name where the error originated.
        context: Optional additional context dict.
    """
    logger.error(
        "error_reported",
        error_type=type(error).__name__,
        error_message=str(error),
        category=category.value,
        module=module,
        context=context or {},
    )
