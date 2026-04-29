"""In-process metrics collection with Prometheus-compatible exposition."""

import time
from collections import defaultdict
from typing import Dict


class _Counter:
    def __init__(self) -> None:
        self._value: float = 0.0

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    @property
    def value(self) -> float:
        return self._value


class _Gauge:
    def __init__(self) -> None:
        self._value: float = 0.0

    def set(self, value: float) -> None:
        self._value = value

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        self._value -= amount

    @property
    def value(self) -> float:
        return self._value


class _Histogram:
    """Simple histogram that tracks sum and count (no buckets)."""

    def __init__(self) -> None:
        self._sum: float = 0.0
        self._count: int = 0

    def observe(self, value: float) -> None:
        self._sum += value
        self._count += 1

    @property
    def mean(self) -> float:
        return self._sum / self._count if self._count else 0.0

    @property
    def count(self) -> int:
        return self._count


class Metrics:
    """Central metrics registry."""

    _counters: Dict[str, _Counter] = defaultdict(_Counter)
    _gauges: Dict[str, _Gauge] = defaultdict(_Gauge)
    _histograms: Dict[str, _Histogram] = defaultdict(_Histogram)

    @classmethod
    def counter(cls, name: str) -> _Counter:
        return cls._counters[name]

    @classmethod
    def gauge(cls, name: str) -> _Gauge:
        return cls._gauges[name]

    @classmethod
    def histogram(cls, name: str) -> _Histogram:
        return cls._histograms[name]

    @classmethod
    def snapshot(cls) -> Dict:
        """Return current metric values as a plain dict."""
        return {
            "counters": {k: v.value for k, v in cls._counters.items()},
            "gauges": {k: v.value for k, v in cls._gauges.items()},
            "histograms": {
                k: {"count": v.count, "mean": v.mean} for k, v in cls._histograms.items()
            },
        }

    @classmethod
    def prometheus_text(cls) -> str:
        """Emit metrics in Prometheus text format."""
        lines = []
        for name, c in cls._counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {c.value}")
        for name, g in cls._gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {g.value}")
        for name, h in cls._histograms.items():
            lines.append(f"# TYPE {name} summary")
            lines.append(f"{name}_count {h.count}")
            lines.append(f"{name}_sum {h._sum}")
        return "\n".join(lines)


class timer:  # noqa: N801 — used as context manager, lowercase intentional
    """Context manager that records elapsed time into a histogram."""

    def __init__(self, metric_name: str) -> None:
        self._name = metric_name
        self._start: float = 0.0

    def __enter__(self) -> "timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        elapsed = time.perf_counter() - self._start
        Metrics.histogram(self._name).observe(elapsed)
