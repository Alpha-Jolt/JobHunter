"""Structured logging setup for JobHunter Scraper Engine."""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class _JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_data", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, default=str)


class Logger:
    """Factory for module-level loggers with consistent configuration."""

    _initialized: bool = False

    @classmethod
    def setup(
        cls,
        level: str = "INFO",
        fmt: str = "json",
        log_dir: Optional[Path] = None,
    ) -> None:
        """Configure root logger once at application startup."""
        if cls._initialized:
            return

        root = logging.getLogger()
        root.setLevel(getattr(logging, level, logging.INFO))

        # Console handler
        console = logging.StreamHandler(sys.stdout)
        if fmt == "json":
            console.setFormatter(_JSONFormatter())
        else:
            console.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")
            )
        root.addHandler(console)

        # File handler (optional)
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "scraper.log", encoding="utf-8")
            file_handler.setFormatter(_JSONFormatter())
            root.addHandler(file_handler)

        cls._initialized = True

    @staticmethod
    def get_logger(name: str) -> "BoundLogger":
        """Return a BoundLogger for the given module name."""
        return BoundLogger(logging.getLogger(name))


class BoundLogger:
    """Thin wrapper that supports structured extra_data on every call."""

    def __init__(self, inner: logging.Logger) -> None:
        self._inner = inner

    def _log(
        self,
        level: int,
        msg: str,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        self._inner.log(
            level,
            msg,
            extra={"extra_data": extra_data or {}},
            exc_info=exc_info,
        )

    def debug(self, msg: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        self._log(logging.DEBUG, msg, extra_data)

    def info(self, msg: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        self._log(logging.INFO, msg, extra_data)

    def warning(self, msg: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        self._log(logging.WARNING, msg, extra_data)

    def error(
        self,
        msg: str,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        self._log(logging.ERROR, msg, extra_data, exc_info=exc_info)

    def critical(
        self,
        msg: str,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        self._log(logging.CRITICAL, msg, extra_data, exc_info=exc_info)
