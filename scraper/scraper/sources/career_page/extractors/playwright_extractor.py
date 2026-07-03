"""Playwright full-render extractor — last-resort JS-rendered career page scraping."""

import logging
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from scraper.sources.career_page.base import BaseCareerExtractor
from scraper.sources.career_page.url_utils import is_job_url

logger = logging.getLogger(__name__)

_PAGE_TIMEOUT = 30_000  # ms
_WAIT_AFTER_LOAD = 2_000  # ms — allow JS to finish rendering


class PlaywrightExtractor(BaseCareerExtractor):
    """Last-resort extractor that fully renders the career page with Playwright.

    Uses JavaScript execution to:
    1. Render the page with all dynamic content
    2. Extract all internal links
    3. Filter by job URL path patterns

    Returns job URL stubs for individual page extraction.
    This extractor is only invoked when all faster strategies fail.
    """

    def get_extraction_method(self) -> str:
        return "playwright_render"

    async def extract(self, company: dict) -> List[dict]:
        """Render the career page and extract all internal job links.

        Args:
            company: Company record dict.

        Returns:
            List of raw job dicts (URL stubs).
        """
        career_url = company.get("career_page_url")
        if not career_url:
            return []

        job_urls = await self._render_and_extract(career_url)
        if not job_urls:
            return []

        jobs = [
            {
                "job_url": url,
                "ats_platform": company.get("ats_platform", "custom"),
                "extraction_method": "playwright_render",
                "company_id": company.get("company_id"),
                "_needs_detail_fetch": True,
            }
            for url in job_urls
        ]
        logger.info(
            "Playwright render extracted job URLs",
            extra={"url": career_url, "jobs": len(jobs)},
        )
        return jobs

    async def _render_and_extract(self, career_url: str) -> List[str]:
        """Render the page and collect internal job URLs.

        Args:
            career_url: Career page URL to render.

        Returns:
            List of unique job URL strings.
        """
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="JobHunterBot/1.0",
                    ignore_https_errors=True,
                )
                page = await context.new_page()

                try:
                    await page.goto(
                        career_url,
                        timeout=_PAGE_TIMEOUT,
                        wait_until="domcontentloaded",
                    )
                    await page.wait_for_timeout(_WAIT_AFTER_LOAD)
                except Exception as exc:
                    logger.debug(
                        "Playwright page load error",
                        extra={"url": career_url, "error": str(exc)},
                    )
                    await browser.close()
                    return []

                # Extract all hrefs from the rendered DOM
                hrefs: List[str] = await page.eval_on_selector_all(
                    "a[href]",
                    "els => els.map(el => el.href)"
                )
                await browser.close()

        except Exception as exc:
            logger.debug(
                "Playwright extractor failed",
                extra={"url": career_url, "error": str(exc)},
            )
            return []

        # Filter for internal job URLs
        base_domain = _extract_domain(career_url)
        job_urls: List[str] = []
        seen: set = set()

        for href in hrefs:
            if not href or not href.startswith("http"):
                continue
            if _extract_domain(href) != base_domain:
                continue
            if not is_job_url(href):
                continue
            if href not in seen:
                seen.add(href)
                job_urls.append(href)

        return job_urls


def _extract_domain(url: str) -> str:
    """Extract the apex domain from a URL for same-domain filtering."""
    try:
        return urlparse(url).netloc.lstrip("www.").lower()
    except Exception:
        return ""
