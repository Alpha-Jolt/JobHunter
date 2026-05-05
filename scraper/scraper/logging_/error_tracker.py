"""Sentry-based error tracking (optional)."""

from typing import Any, Optional


class ErrorTracker:
    """Thin wrapper around Sentry SDK. No-ops when DSN is not configured."""

    _enabled: bool = False

    @classmethod
    def setup(cls, dsn: Optional[str], sample_rate: float = 0.2) -> None:
        """Initialise Sentry if DSN is provided."""
        if not dsn:
            return
        try:
            import sentry_sdk  # noqa: PLC0415

            sentry_sdk.init(dsn=dsn, traces_sample_rate=sample_rate)
            cls._enabled = True
        except ImportError:
            pass

    @classmethod
    def capture_exception(cls, exc: Exception, **context: Any) -> None:
        """Capture exception with optional context tags."""
        if not cls._enabled:
            return
        try:
            import sentry_sdk  # noqa: PLC0415

            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_tag(key, str(value))
                sentry_sdk.capture_exception(exc)
        except Exception:
            pass

    @classmethod
    def capture_message(cls, msg: str, level: str = "info", **context: Any) -> None:
        """Capture a plain message."""
        if not cls._enabled:
            return
        try:
            import sentry_sdk  # noqa: PLC0415

            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_tag(key, str(value))
                sentry_sdk.capture_message(msg, level=level)
        except Exception:
            pass
