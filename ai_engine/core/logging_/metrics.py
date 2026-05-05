"""In-process metrics counters for observability."""

from __future__ import annotations

from collections import defaultdict
from threading import Lock


class MetricsCollector:
    """Thread-safe counter-based metrics collector.

    Tracks counts and latency totals per event key.
    Designed to be replaced by a proper metrics backend (Prometheus, etc.) in Phase 1+.
    """

    def __init__(self) -> None:
        self._counts: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def increment(self, key: str, value: int = 1) -> None:
        """Increment a counter.

        Args:
            key: Metric key (e.g. 'llm.calls.anthropic').
            value: Amount to increment by.
        """
        with self._lock:
            self._counts[key] += value

    def record_latency(self, key: str, seconds: float) -> None:
        """Record a latency observation.

        Args:
            key: Metric key (e.g. 'llm.latency.anthropic').
            seconds: Elapsed time in seconds.
        """
        with self._lock:
            self._latencies[key].append(seconds)

    def get_count(self, key: str) -> int:
        """Return current count for a key."""
        return self._counts.get(key, 0)

    def get_avg_latency(self, key: str) -> float | None:
        """Return average latency for a key, or None if no data."""
        values = self._latencies.get(key)
        if not values:
            return None
        return sum(values) / len(values)

    def snapshot(self) -> dict[str, int | float]:
        """Return a flat snapshot of all metrics."""
        with self._lock:
            result: dict[str, int | float] = dict(self._counts)
            for key, values in self._latencies.items():
                if values:
                    result[f"{key}.avg_latency"] = sum(values) / len(values)
            return result


# Module-level singleton
metrics = MetricsCollector()
