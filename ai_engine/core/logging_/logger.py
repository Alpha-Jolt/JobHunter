"""Structured logging setup for the AI Engine."""

from __future__ import annotations

import logging
import sys
from typing import Any

try:
    import structlog

    _STRUCTLOG_AVAILABLE = True
except ImportError:
    _STRUCTLOG_AVAILABLE = False


def _configure_structlog(level: str) -> None:
    """Configure structlog with JSON rendering."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )


def _configure_stdlib(level: str, fmt: str) -> None:
    """Configure stdlib logging as fallback."""
    if fmt == "text":
        log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    else:
        log_format = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=log_format,
        stream=sys.stdout,
    )


def setup_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Initialise logging for the AI Engine.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        fmt: Output format — 'json' or 'text'.
    """
    if _STRUCTLOG_AVAILABLE and fmt == "json":
        _configure_structlog(level)
    else:
        _configure_stdlib(level, fmt)


def get_logger(name: str) -> Any:
    """Return a logger for the given module name.

    Args:
        name: Module name, typically ``__name__``.

    Returns:
        structlog bound logger or stdlib Logger.
    """
    if _STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    return logging.getLogger(name)
