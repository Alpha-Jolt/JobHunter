"""Unit tests for RateLimiter."""

import asyncio
import time

import pytest

from scraper.core.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_acquire_no_limit_configured():
    rl = RateLimiter()
    # Should not block when no rate is set
    start = time.monotonic()
    await rl.acquire("unknown.domain")
    assert time.monotonic() - start < 0.1


@pytest.mark.asyncio
async def test_acquire_respects_rate():
    rl = RateLimiter()
    rl.set_rate("test.domain", 10.0)  # 10 rps — fast enough for tests
    start = time.monotonic()
    for _ in range(5):
        await rl.acquire("test.domain")
    elapsed = time.monotonic() - start
    assert elapsed < 2.0  # Should complete quickly with burst capacity
