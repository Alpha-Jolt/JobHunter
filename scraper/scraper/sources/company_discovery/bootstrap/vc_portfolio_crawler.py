"""VC and accelerator portfolio crawler — extracts company domains from portfolio pages."""

import asyncio
import logging
from typing import List

from playwright.async_api import async_playwright

from scraper.sources.company_discovery.base import BaseCompanySource
from scraper.sources.company_discovery.enrichment.domain_utils import (
    is_job_board,
    normalize_apex_domain,
)
from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker

logger = logging.getLogger(__name__)

_PAGE_TIMEOUT = 30_000  # ms
_RATE_LIMIT_KEY = "vc_portfolio"

# Known social/aggregator domains to discard from portfolio page links
_DISCARD_DOMAINS = frozenset([
    "linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com",
    "github.com", "crunchbase.com", "angel.co", "wellfound.com",
    "medium.com", "substack.com", "youtube.com",
])

VC_PORTFOLIO_PAGES = [
    {"name": "Sequoia India", "url": "https://www.sequoiacap.com/india/"},
    {"name": "Accel India", "url": "https://www.accel.com/companies"},
    {"name": "Nexus VP", "url": "https://nexusvp.com/portfolio/"},
    {"name": "Kalaari Capital", "url": "https://www.kalaari.com/portfolio/"},
    {"name": "Matrix Partners India", "url": "https://www.matrixpartners.in/portfolio/"},
    {"name": "Blume Ventures", "url": "https://blume.vc/portfolio"},
    {"name": "100X.VC", "url": "https://www.100x.vc/portfolio"},
    {"name": "Venture Catalysts", "url": "https://venturecatalysts.in/portfolio"},
    {"name": "CIIE.CO", "url": "https://ciie.co/portfolio/"},
    {"name": "NASSCOM 10000 Startups", "url": "https://nasscom.in/10000startups/"},
    {"name": "IIT Madras Incubation Cell", "url": "https://icf.iitmadras.org/portfolio/"},
    {"name": "IIT Bombay SINE", "url": "https://www.sineiitb.org/startups/"},
    {"name": "IIT Delhi FITT", "url": "https://fitt-iitd.org/startups/"},
]


class VCPortfolioCrawler(BaseCompanySource):
    """Crawls VC and accelerator portfolio pages for company domains.

    Uses Playwright for JS-rendered portfolio pages. Respects robots.txt
    before loading each page.

    Args:
        robots_checker: Shared RobotsChecker instance.
    """

    def __init__(self, robots_checker: RobotsChecker, **kwargs) -> None:
        super().__init__(**kwargs)
        self._robots_checker = robots_checker

    def get_source_tag(self) -> str:
        return "vc_portfolio"

    async def discover(self, **kwargs) -> List[str]:
        """Crawl all VC portfolio pages and return discovered domains.

        Returns:
            List of unique, normalised apex domain strings.
        """
        all_domains: List[str] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="JobHunterBot/1.0",
                ignore_https_errors=True,
            )

            for vc in VC_PORTFOLIO_PAGES:
                try:
                    domains = await self._crawl_portfolio_page(context, vc)
                    logger.info(
                        "VC portfolio crawled",
                        extra={"vc": vc["name"], "domains": len(domains)},
                    )
                    all_domains.extend(domains)
                    await self.rate_limiter.wait(_RATE_LIMIT_KEY)
                except Exception as exc:
                    logger.warning(
                        "VC portfolio crawl failed",
                        extra={"vc": vc["name"], "error": str(exc)},
                    )

            await browser.close()

        # Deduplicate
        seen: set = set()
        unique: List[str] = []
        for d in all_domains:
            if d and d not in seen:
                seen.add(d)
                unique.append(d)

        logger.info(
            "VC portfolio discovery complete",
            extra={"total_unique_domains": len(unique)},
        )
        return unique

    async def _crawl_portfolio_page(self, context, vc: dict) -> List[str]:
        """Crawl a single VC portfolio page for external company links.

        Args:
            context: Playwright browser context.
            vc: Dict with ``name`` and ``url`` keys.

        Returns:
            List of normalised apex domain strings from the page.
        """
        vc_url = vc["url"]

        # robots.txt check
        from urllib.parse import urlparse
        parsed = urlparse(vc_url)
        vc_domain = parsed.netloc.lstrip("www.")
        if not await self._robots_checker.is_allowed(vc_domain, parsed.path or "/"):
            logger.info("robots.txt blocked VC portfolio", extra={"vc": vc["name"]})
            return []

        page = await context.new_page()
        try:
            await page.goto(vc_url, timeout=_PAGE_TIMEOUT, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)  # allow JS to render

            # Extract all external hrefs
            hrefs: List[str] = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(el => el.href)"
            )
        except Exception as exc:
            logger.debug(
                "Portfolio page load failed",
                extra={"vc": vc["name"], "error": str(exc)},
            )
            return []
        finally:
            await page.close()

        domains: List[str] = []
        vc_apex = normalize_apex_domain(vc_url)

        for href in hrefs:
            if not href or not href.startswith("http"):
                continue
            apex = normalize_apex_domain(href)
            if not apex:
                continue
            # Exclude the VC's own domain and known aggregators
            if apex == vc_apex:
                continue
            if apex in _DISCARD_DOMAINS or is_job_board(apex):
                continue
            domains.append(apex)

        return domains
