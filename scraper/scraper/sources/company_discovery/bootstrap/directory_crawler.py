"""Public directory crawler — extracts company domains from Zauba Corp, NASSCOM, CII."""

import logging
import string
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from scraper.sources.company_discovery.base import BaseCompanySource
from scraper.sources.company_discovery.enrichment.domain_utils import (
    is_job_board,
    normalize_apex_domain,
)
from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 15.0
_RATE_LIMIT_KEY = "directory"
_PAGE_TIMEOUT = 30_000  # ms

# Zauba Corp alphabetical listing URL pattern
_ZAUBA_LIST_URL = "https://www.zaubacorp.com/companysearch/company-list-{letter}-page-{page}.html"

# NASSCOM public member directory
_NASSCOM_URL = "https://nasscom.in/member-directory/"

# CII public member listing
_CII_URL = "https://www.cii.in/MemberDirectory.aspx"


class DirectoryCrawler(BaseCompanySource):
    """Crawls public business directories for Indian company domains.

    Targets: Zauba Corp, NASSCOM, CII public sections only.
    robots.txt is checked before crawling each directory.

    Args:
        robots_checker: Shared RobotsChecker instance.
        max_zauba_pages_per_letter: Maximum pages to fetch per letter in Zauba.
            Set lower in development to avoid long crawls.
    """

    def __init__(
        self,
        robots_checker: RobotsChecker,
        max_zauba_pages_per_letter: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._robots_checker = robots_checker
        self._max_zauba_pages_per_letter = max_zauba_pages_per_letter

    def get_source_tag(self) -> str:
        return "directory"

    async def discover(self, **kwargs) -> List[str]:
        """Crawl all configured directories and return discovered domains.

        Returns:
            List of unique, normalised apex domain strings.
        """
        all_domains: List[str] = []

        zauba_domains = await self._crawl_zauba()
        logger.info(
            "Zauba Corp crawled", extra={"domains": len(zauba_domains)}
        )
        all_domains.extend(zauba_domains)

        nasscom_domains = await self._crawl_nasscom()
        logger.info(
            "NASSCOM directory crawled", extra={"domains": len(nasscom_domains)}
        )
        all_domains.extend(nasscom_domains)

        cii_domains = await self._crawl_cii()
        logger.info(
            "CII directory crawled", extra={"domains": len(cii_domains)}
        )
        all_domains.extend(cii_domains)

        seen: set = set()
        unique: List[str] = []
        for d in all_domains:
            if d and d not in seen:
                seen.add(d)
                unique.append(d)

        logger.info(
            "Directory discovery complete",
            extra={"total_unique_domains": len(unique)},
        )
        return unique

    async def _crawl_zauba(self) -> List[str]:
        """Crawl Zauba Corp company listings.

        Only extracts company names and links — Zauba records link to company
        detail pages that may contain website domains.

        Returns:
            List of apex domain strings.
        """
        if not await self._robots_checker.is_allowed("www.zaubacorp.com", "/"):
            logger.info("Zauba Corp robots.txt blocked")
            return []

        domains: List[str] = []

        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "JobHunterBot/1.0"},
        ) as client:
            for letter in string.ascii_uppercase:
                for page in range(1, self._max_zauba_pages_per_letter + 1):
                    url = _ZAUBA_LIST_URL.format(letter=letter, page=page)
                    page_domains = await self._extract_domains_from_listing(client, url)
                    if not page_domains:
                        break  # no more pages for this letter
                    domains.extend(page_domains)
                    await self.rate_limiter.wait(_RATE_LIMIT_KEY)

        return domains

    async def _extract_domains_from_listing(
        self, client: httpx.AsyncClient, url: str
    ) -> List[str]:
        """Fetch a listing page and extract company website domains.

        Args:
            client: Shared httpx client.
            url: Listing page URL.

        Returns:
            List of apex domain strings.
        """
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return []
            html = resp.text
        except Exception as exc:
            logger.debug(
                "Zauba page fetch failed",
                extra={"url": url, "error": str(exc)},
            )
            return []

        soup = BeautifulSoup(html, "lxml")
        domains: List[str] = []

        # Zauba detail links typically contain the company domain or CIN
        # Extract external links from the page that may be company websites
        for anchor in soup.find_all("a", href=True):
            href: str = anchor["href"]
            if not href.startswith("http"):
                continue
            # Skip Zauba's own domain
            if "zaubacorp.com" in href:
                continue
            apex = normalize_apex_domain(href)
            if apex and not is_job_board(apex):
                domains.append(apex)

        return domains

    async def _crawl_nasscom(self) -> List[str]:
        """Crawl the public NASSCOM member directory.

        Uses Playwright for JS-rendered pagination.

        Returns:
            List of apex domain strings.
        """
        if not await self._robots_checker.is_allowed("nasscom.in", "/member-directory/"):
            logger.info("NASSCOM robots.txt blocked")
            return []

        domains: List[str] = []
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context(user_agent="JobHunterBot/1.0")
                page = await context.new_page()
                await page.goto(
                    _NASSCOM_URL,
                    timeout=_PAGE_TIMEOUT,
                    wait_until="domcontentloaded",
                )
                await page.wait_for_timeout(2000)

                # Extract all external links on the page
                hrefs: List[str] = await page.eval_on_selector_all(
                    "a[href]",
                    "els => els.map(el => el.href)"
                )
                await browser.close()

            for href in hrefs:
                if not href or "nasscom.in" in href:
                    continue
                apex = normalize_apex_domain(href)
                if apex and not is_job_board(apex):
                    domains.append(apex)

        except Exception as exc:
            logger.warning(
                "NASSCOM directory crawl failed",
                extra={"error": str(exc)},
            )

        return domains

    async def _crawl_cii(self) -> List[str]:
        """Crawl the public CII member directory.

        Returns:
            List of apex domain strings.
        """
        if not await self._robots_checker.is_allowed("www.cii.in", "/MemberDirectory.aspx"):
            logger.info("CII robots.txt blocked")
            return []

        domains: List[str] = []
        try:
            async with httpx.AsyncClient(
                timeout=_HTTP_TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": "JobHunterBot/1.0"},
            ) as client:
                resp = await client.get(_CII_URL)
                if resp.status_code != 200:
                    return []
                soup = BeautifulSoup(resp.text, "lxml")

                for anchor in soup.find_all("a", href=True):
                    href: str = anchor["href"]
                    if not href.startswith("http"):
                        continue
                    if "cii.in" in href:
                        continue
                    apex = normalize_apex_domain(href)
                    if apex and not is_job_board(apex):
                        domains.append(apex)

        except Exception as exc:
            logger.warning(
                "CII directory crawl failed",
                extra={"error": str(exc)},
            )

        return domains
