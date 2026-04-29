"""Proxy rotation with health checking and failure tracking."""

import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

import httpx

from scraper.logging_.logger import Logger


class ProxyStrategy(str, Enum):
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED = "weighted"


class ProxyManager:
    """Rotates proxies, tracks failures, and falls back to direct connection."""

    def __init__(
        self,
        proxy_list: List[str],
        strategy: ProxyStrategy = ProxyStrategy.ROUND_ROBIN,
        health_check_interval: int = 3600,
        max_failures: int = 3,
        fallback_to_direct: bool = True,
    ) -> None:
        self.proxy_list = list(proxy_list)
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self.fallback_to_direct = fallback_to_direct
        self._index: int = 0
        self._failures: Dict[str, int] = {p: 0 for p in proxy_list}
        self._last_check: Dict[str, datetime] = {}
        self.logger = Logger.get_logger(__name__)

    async def get_proxy(self) -> Optional[str]:
        """Return next healthy proxy, or None for direct connection."""
        if not self.proxy_list:
            return None

        available = [p for p in self.proxy_list if self._failures.get(p, 0) < self.max_failures]
        if not available:
            if self.fallback_to_direct:
                self.logger.warning("All proxies exhausted — using direct connection")
                return None
            raise RuntimeError("No healthy proxies available")

        proxy = self._select(available)

        if self._needs_health_check(proxy):
            healthy = await self._check_proxy_health(proxy)
            if not healthy:
                self.record_failure(proxy)
                return await self.get_proxy()

        return proxy

    def _select(self, available: List[str]) -> str:
        if self.strategy == ProxyStrategy.RANDOM:
            return random.choice(available)
        if self.strategy == ProxyStrategy.WEIGHTED:
            weights = [self.max_failures - self._failures.get(p, 0) for p in available]
            return random.choices(available, weights=weights, k=1)[0]
        # ROUND_ROBIN
        proxy = available[self._index % len(available)]
        self._index += 1
        return proxy

    async def _check_proxy_health(self, proxy: str) -> bool:
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=10.0) as client:
                resp = await client.head("https://httpbin.org/get")
                self._last_check[proxy] = datetime.now()
                return resp.status_code < 500
        except Exception as exc:
            self.logger.warning(
                "Proxy health check failed",
                extra_data={"proxy": proxy, "error": str(exc)},
            )
            self._last_check[proxy] = datetime.now()
            return False

    def _needs_health_check(self, proxy: str) -> bool:
        last = self._last_check.get(proxy)
        if last is None:
            return True
        return datetime.now() - last > timedelta(seconds=self.health_check_interval)

    def record_failure(self, proxy: str) -> None:
        """Increment failure counter for a proxy."""
        self._failures[proxy] = self._failures.get(proxy, 0) + 1
        self.logger.warning(
            "Proxy failure recorded",
            extra_data={
                "proxy": proxy,
                "failures": self._failures[proxy],
            },
        )

    def record_success(self, proxy: str) -> None:
        """Decrement failure counter on success."""
        if self._failures.get(proxy, 0) > 0:
            self._failures[proxy] -= 1
