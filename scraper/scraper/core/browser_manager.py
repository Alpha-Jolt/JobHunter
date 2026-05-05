"""Playwright browser lifecycle management with pooling and stealth."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    async_playwright,
)
from playwright_stealth import Stealth

from scraper.logging_.logger import Logger

_STEALTH = Stealth()

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

_VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
]

# Overrides Sec-Ch-Ua to hide HeadlessChrome fingerprint
_STEALTH_HEADERS = {
    "Sec-Ch-Ua": ('"Google Chrome";v="124", "Chromium";v="124", "Not-A.Brand";v="99"'),
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}


class BrowserManager:
    """Manages a pool of Playwright Chromium browsers with stealth."""

    def __init__(
        self,
        headless: bool = True,
        pool_size: int = 3,
        timeout_ms: int = 30_000,
        enable_stealth: bool = True,
        debug_screenshots: bool = False,
        debug_dir: Path = Path("logs"),
    ) -> None:
        self.headless = headless
        self.pool_size = pool_size
        self.timeout_ms = timeout_ms
        self.enable_stealth = enable_stealth
        self.debug_screenshots = debug_screenshots
        self.debug_dir = debug_dir
        self._browsers: List[Browser] = []
        self._playwright = None
        self._lock = asyncio.Lock()
        self._round_robin = 0
        self.logger = Logger.get_logger(__name__)

    async def initialize(self) -> None:
        """Start Playwright and launch browser pool."""
        self._playwright = await async_playwright().start()
        for i in range(self.pool_size):
            browser = await self._launch_browser()
            self._browsers.append(browser)
            self.logger.debug("Browser initialised", extra_data={"index": i})
        self.logger.info(
            "Browser pool ready",
            extra_data={"pool_size": self.pool_size},
        )

    async def _launch_browser(self) -> Browser:
        return await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",  # required on Linux/WSL
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

    async def get_page(self, source: str) -> Page:
        """Return a new isolated page from the pool (round-robin)."""
        if not self._browsers:
            raise RuntimeError("BrowserManager not initialised — call initialize() first")

        async with self._lock:
            browser = self._browsers[self._round_robin % len(self._browsers)]
            self._round_robin += 1

        import random  # noqa: PLC0415

        viewport = random.choice(_VIEWPORTS)
        user_agent = random.choice(_USER_AGENTS)

        context: BrowserContext = await browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            extra_http_headers=_STEALTH_HEADERS,
        )
        if self.enable_stealth:
            await _STEALTH.apply_stealth_async(context)

        page = await context.new_page()
        page.set_default_timeout(self.timeout_ms)

        self.logger.debug("Page created", extra_data={"source": source})
        return page

    async def screenshot_for_debug(self, page: Page, source: str, identifier: str) -> Optional[str]:
        """Save a debug screenshot if debug_screenshots is enabled."""
        if not self.debug_screenshots:
            return None
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = str(self.debug_dir / f"debug_{source}_{identifier}_{ts}.png")
        try:
            await page.screenshot(path=path)
            return path
        except Exception as exc:
            self.logger.warning("Screenshot failed", extra_data={"error": str(exc)})
            return None

    async def restart_browser(self, index: int) -> None:
        """Replace a crashed browser at the given pool index."""
        if index >= len(self._browsers):
            return
        try:
            await self._browsers[index].close()
        except Exception:
            pass
        self._browsers[index] = await self._launch_browser()
        self.logger.info("Browser restarted", extra_data={"index": index})

    async def close_all(self) -> None:
        """Close all browsers and stop Playwright."""
        for browser in self._browsers:
            try:
                await browser.close()
            except Exception as exc:
                self.logger.error(
                    "Error closing browser",
                    extra_data={"error": str(exc)},
                )
        self._browsers.clear()
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                # Suppress errors when the event loop is shutting down
                pass
        self.logger.info("All browsers closed")

    async def __aenter__(self) -> "BrowserManager":
        await self.initialize()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close_all()
