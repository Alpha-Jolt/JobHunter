"""Exponential backoff retry handler with circuit breaker."""

import asyncio
import random
from enum import Enum
from typing import Any, Callable, Optional

from scraper.logging_.logger import Logger


class ErrorSeverity(str, Enum):
    RECOVERABLE = "recoverable"  # Retry immediately
    TRANSIENT = "transient"  # Retry with backoff
    NON_RECOVERABLE = "non_recoverable"  # Do not retry


_TRANSIENT_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
)

_NON_RECOVERABLE_MESSAGES = (
    "403",
    "404",
    "blocked",
    "captcha",
)


class RetryHandler:
    """Execute coroutines with exponential backoff and circuit breaker."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        circuit_breaker_threshold: int = 5,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self._consecutive_failures: int = 0
        self._circuit_open: bool = False
        self.logger = Logger.get_logger(__name__)

    async def execute_with_retry(
        self,
        coro_func: Callable,
        *args: Any,
        error_handler: Optional[Callable] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Call coro_func(*args, **kwargs) with retry logic.

        Args:
            coro_func: Async callable to execute.
            error_handler: Optional callable(exc) → ErrorSeverity override.
        """
        if self._circuit_open:
            raise RuntimeError("Circuit breaker is open — too many consecutive failures")

        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                result = await coro_func(*args, **kwargs)
                self._consecutive_failures = 0
                self._circuit_open = False
                return result
            except Exception as exc:
                last_exc = exc
                severity = error_handler(exc) if error_handler else self._classify_error(exc)

                if severity == ErrorSeverity.NON_RECOVERABLE:
                    self.logger.error(
                        "Non-recoverable error — aborting",
                        extra_data={"error": str(exc), "attempt": attempt},
                        exc_info=True,
                    )
                    raise

                if attempt >= self.max_retries:
                    break

                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    "Retrying after error",
                    extra_data={
                        "error": str(exc),
                        "attempt": attempt + 1,
                        "delay_s": round(delay, 2),
                    },
                )
                await asyncio.sleep(delay)

        self._consecutive_failures += 1
        if self._consecutive_failures >= self.circuit_breaker_threshold:
            self._circuit_open = True
            self.logger.error(
                "Circuit breaker opened",
                extra_data={"consecutive_failures": self._consecutive_failures},
            )

        raise last_exc  # type: ignore[misc]

    def _calculate_delay(self, attempt: int) -> float:
        """Exponential backoff with ±25 % jitter."""
        delay = min(self.base_delay * (2**attempt), self.max_delay)
        jitter = delay * 0.25 * (random.random() * 2 - 1)
        return max(0.0, delay + jitter)

    def _classify_error(self, exc: Exception) -> ErrorSeverity:
        msg = str(exc).lower()
        if any(kw in msg for kw in _NON_RECOVERABLE_MESSAGES):
            return ErrorSeverity.NON_RECOVERABLE
        if isinstance(exc, _TRANSIENT_EXCEPTIONS):
            return ErrorSeverity.TRANSIENT
        return ErrorSeverity.RECOVERABLE

    def reset_circuit(self) -> None:
        """Manually reset circuit breaker (e.g. after proxy rotation)."""
        self._circuit_open = False
        self._consecutive_failures = 0
