"""Hunter.io domain search scraper."""

from typing import List, Optional

import httpx

from scraper.config import config
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.base_scraper import BaseScraper


class HunterScraper(BaseScraper):
    """Scrapes company domains via Hunter.io API for emails."""

    def __init__(
        self,
        rate_limiter: RateLimiter,
        retry_handler: RetryHandler,
        debug: bool = False,
    ) -> None:
        super().__init__(rate_limiter, retry_handler, debug)
        self.api_key = config.hunter_api_key

    async def initialize(self) -> None:
        if not self.api_key:
            self.logger.warning("Hunter API key is not configured.")
        self.client = httpx.AsyncClient(timeout=15.0)

    async def close(self) -> None:
        if hasattr(self, "client"):
            await self.client.aclose()

    def get_source_name(self) -> str:
        return "hunter"

    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        domains: Optional[List[str]] = None,
        **kwargs,
    ) -> List[IntermediateJob]:
        """Fetch emails for domains using Hunter.io. keywords and locations are ignored."""
        if not domains:
            self.logger.info("No domains provided for Hunter.io scrape.")
            return []

        results: List[IntermediateJob] = []

        for domain in domains:
            try:
                jobs = await self.retry_handler.execute_with_retry(
                    self._scrape_domain, domain
                )
                results.extend(jobs)
            except Exception as e:
                self.logger.error(f"Hunter scrape failed for {domain}", extra_data={"error": str(e)})

        return results

    async def _scrape_domain(self, domain: str) -> List[IntermediateJob]:
        if not self.api_key:
            raise ValueError("HUNTER_API_KEY is required but not set.")

        await self.rate_limiter.acquire("hunter")

        url = "https://api.hunter.io/v2/domain-search"
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "type": "personal",
            "limit": 10,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})

        company_name = data.get("organization", domain)
        emails = data.get("emails", [])
        
        # Filter for HR/Recruiting if possible
        hr_emails = []
        for e in emails:
            dep = e.get("department")
            if dep in ("hr", "recruiting", "human resources", "executive") or e.get("type") == "personal":
                hr_emails.append(e.get("value"))

        if not hr_emails:
            return []

        # Return a single synthetic job per domain with the primary HR email
        job = IntermediateJob(
            source=self.get_source_name(),
            external_id=f"{domain}:{hr_emails[0]}",
            raw_url=f"https://{domain}",
            company_name=company_name,
            company_domain=domain,
            apply_email_raw=hr_emails[0],
            title="",
            description="",
        )
        return [job]
