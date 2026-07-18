"""Apify generic actor scraper for job listings."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from scraper.config import config
from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.apify_field_maps import ACTOR_FIELD_MAPS
from scraper.sources.base_scraper import BaseScraper


class ApifyScraper(BaseScraper):
    """Orchestrates Apify actors to scrape domains/queries for jobs."""

    def __init__(
        self,
        rate_limiter: RateLimiter,
        retry_handler: RetryHandler,
        debug: bool = False,
    ) -> None:
        super().__init__(rate_limiter, retry_handler, debug)
        self.api_token = config.apify_api_token
        self.timeout_sec = config.apify_run_timeout_seconds
        self.poll_interval = config.apify_poll_interval_seconds

    async def initialize(self) -> None:
        if not self.api_token:
            self.logger.warning("Apify API token is not configured.")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        if hasattr(self, "client"):
            await self.client.aclose()

    def get_source_name(self) -> str:
        return "apify"

    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        domains: Optional[List[str]] = None,
        actor_id: str = "apify/indeed-scraper",
        actor_input: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[IntermediateJob]:
        """Trigger an Apify actor and wait for results."""
        if not self.api_token:
            self.logger.error("APIFY_API_TOKEN is not set.")
            return []

        await self.rate_limiter.acquire("apify")

        if not actor_input:
            # Construct a default input based on actor type if none provided
            actor_input = self._build_default_input(actor_id, keywords, locations, domains)

        # 1. Start the Actor run
        start_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={self.api_token}"
        try:
            start_resp = await self.client.post(start_url, json=actor_input)
            start_resp.raise_for_status()
            run_data = start_resp.json().get("data", {})
            run_id = run_data.get("id")
            if not run_id:
                self.logger.error("Apify did not return a run ID.", extra_data={"resp": run_data})
                return []
            
            self.logger.info(f"Apify actor {actor_id} started. Run ID: {run_id}")
        except Exception as e:
            self.logger.error("Failed to start Apify actor", extra_data={"error": str(e), "actor_id": actor_id})
            return []

        # 2. Poll for completion
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.api_token}"
        start_time = datetime.now(timezone.utc)
        
        while True:
            await asyncio.sleep(self.poll_interval)
            
            if (datetime.now(timezone.utc) - start_time).total_seconds() > self.timeout_sec:
                self.logger.error(f"Apify run {run_id} timed out.")
                # Optional: Abort run via API here
                return []

            try:
                stat_resp = await self.client.get(status_url)
                stat_resp.raise_for_status()
                status_data = stat_resp.json().get("data", {})
                status = status_data.get("status")
                
                if status == "SUCCEEDED":
                    dataset_id = status_data.get("defaultDatasetId")
                    break
                elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    self.logger.error(f"Apify run {run_id} ended with status: {status}")
                    return []
            except Exception as e:
                self.logger.error(f"Error polling Apify run {run_id}", extra_data={"error": str(e)})

        # 3. Fetch Dataset
        if not dataset_id:
            return []

        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.api_token}"
        try:
            data_resp = await self.client.get(dataset_url)
            data_resp.raise_for_status()
            items = data_resp.json()
            return self._map_dataset_to_intermediate(actor_id, items)
        except Exception as e:
            self.logger.error(f"Failed to fetch Apify dataset {dataset_id}", extra_data={"error": str(e)})
            return []

    def _build_default_input(self, actor_id: str, keywords: List[str], locations: List[str], domains: Optional[List[str]]) -> Dict[str, Any]:
        """Build input JSON based on the actor."""
        # Simple indeed scraper payload
        if "indeed" in actor_id.lower():
            position = keywords[0] if keywords else "software engineer"
            location = locations[0] if locations else "remote"
            return {
                "position": position,
                "country": "US",
                "location": location,
                "maxItems": 10,
                "parseCompanyDetails": False
            }
        # Simple naukri payload
        elif "naukri" in actor_id.lower():
            return {
                "keywords": keywords[0] if keywords else "developer",
                "location": locations[0] if locations else "remote",
                "maxItems": 10
            }
        return {}

    def _map_dataset_to_intermediate(self, actor_id: str, items: List[Dict[str, Any]]) -> List[IntermediateJob]:
        """Map generic Apify JSON output to IntermediateJob using ACTOR_FIELD_MAPS."""
        field_map = ACTOR_FIELD_MAPS.get(actor_id, ACTOR_FIELD_MAPS["default"])
        results = []

        for item in items:
            def extract(keys: List[str]) -> Optional[Any]:
                for k in keys:
                    if k in item and item[k]:
                        return item[k]
                return None

            title = extract(field_map.get("title", [])) or "Unknown Title"
            company = extract(field_map.get("company_name", [])) or "Unknown Company"
            url = extract(field_map.get("apply_url", [])) or ""
            
            # Use Apify dataset item ID as part of external ID if available
            item_id = item.get("id") or item.get("objectID")
            import hashlib
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            ext_id = f"{item_id}:{url_hash}" if item_id else url_hash

            job = IntermediateJob(
                source=actor_id,
                external_id=ext_id,
                raw_url=url,
                title=title,
                company_name=company,
                location_raw=extract(field_map.get("location", [])),
                description=extract(field_map.get("description", [])),
                salary_raw=extract(field_map.get("salary_raw", [])),
                posted_date_raw=extract(field_map.get("posted_date", [])),
                job_type_raw=extract(field_map.get("job_type", [])),
                extraction_source="json_api",
                extra_raw=item,  # Preserve original item
            )
            results.append(job)

        return results
