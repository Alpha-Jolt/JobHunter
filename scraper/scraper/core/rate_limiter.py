"""Token-bucket rate limiter with per-domain tracking."""

import asyncio
from datetime import datetime
from typing import Dict

from scraper.logging_.logger import Logger


class _TokenBucket:
    """Single token bucket for one domain."""

    def __init__(self, capacity: float, refill_rate: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self._last_refill = datetime.now()

    def _refill(self) -> None:
        now = datetime.now()
        elapsed = (now - self._last_refill).total_seconds()
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self._last_refill = now

    async def acquire(self, tokens: float = 1.0) -> None:
        """Wait until enough tokens are available, then consume them."""
        while True:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return
            wait = (tokens - self.tokens) / self.refill_rate
            await asyncio.sleep(wait)


class RateLimiter:
    """Per-domain rate limiter backed by token buckets."""

    def __init__(self) -> None:
        self._buckets: Dict[str, _TokenBucket] = {}
        self.logger = Logger.get_logger(__name__)

    def set_rate(self, domain: str, requests_per_second: float) -> None:
        """Configure rate for a domain (capacity = 2x rate for burst)."""
        capacity = requests_per_second * 2
        self._buckets[domain] = _TokenBucket(capacity, requests_per_second)
        self.logger.debug(
            "Rate set",
            extra_data={"domain": domain, "rps": requests_per_second},
        )

    async def acquire(self, domain: str, tokens: float = 1.0) -> None:
        """Block until a token is available for the given domain."""
        if domain not in self._buckets:
            # No limit configured — allow immediately
            return
        await self._buckets[domain].acquire(tokens)
