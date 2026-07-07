"""Dataset importer — bulk imports company domains from open-source public datasets."""

import csv
import io
import logging
from typing import List

import httpx

from scraper.config import config
from scraper.sources.company_discovery.base import BaseCompanySource
from scraper.sources.company_discovery.enrichment.domain_utils import (
    is_job_board,
    normalize_apex_domain,
)

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 30.0

# Public open-source company datasets (no authentication required)
_GITHUB_CSV_SOURCES = [
    {
        "name": "github_india_startups_csv",
        "url": (
            "https://raw.githubusercontent.com/datasets/tech-companies-india/"
            "master/data.csv"
        ),
        "domain_col": "domain",
        "name_col": "company",
    },
]

_STARTUP_INDIA_API = (
    "https://api.startupindia.gov.in/sih/api/noauth/search/profiles"
)
_STARTUP_INDIA_PAGE_SIZE = 50

# data.gov.in MSME UDYAM registered units — bulk open resource, no scraping.
# Credentials and pagination limits are read from config (env vars).
_DATAGOV_API_BASE = "https://api.data.gov.in/resource"

# data.gov.in MCA21 resource ID (public, no auth required for open resources)
_MCA21_API_BASE = "https://api.data.gov.in/resource"
_MCA21_RESOURCE_ID = "64b1ecfd-8a52-40ab-954c-fc87f61f4e23"
_MCA21_PAGE_SIZE = 500


class DatasetImporter(BaseCompanySource):
    """Imports company domains from publicly available bulk datasets.

    Includes:
    - GitHub open-source company CSV lists
    - Startup India portal API
    - MCA21 bulk company data via data.gov.in

    All sources require no authentication or scraping of company servers.
    """

    def get_source_tag(self) -> str:
        return "bootstrap_dataset"

    async def discover(self, **kwargs) -> List[str]:
        """Return apex domains collected from all dataset sources.

        Returns:
            List of unique, normalised apex domain strings.
        """
        all_domains: List[str] = []

        for source_def in _GITHUB_CSV_SOURCES:
            domains = await self._import_csv_source(source_def)
            logger.info(
                "GitHub CSV imported",
                extra={"source": source_def["name"], "domains": len(domains)},
            )
            all_domains.extend(domains)

        startup_india_domains = await self._import_startup_india()
        logger.info(
            "Startup India imported",
            extra={"domains": len(startup_india_domains)},
        )
        all_domains.extend(startup_india_domains)

        msme_domains = await self._import_msme_udyam()
        logger.info(
            "MSME UDYAM bulk import complete",
            extra={"domains": len(msme_domains)},
        )
        all_domains.extend(msme_domains)

        # Deduplicate at this stage before returning to the queue
        seen: set = set()
        unique: List[str] = []
        for d in all_domains:
            if d and d not in seen:
                seen.add(d)
                unique.append(d)

        logger.info(
            "Dataset import complete",
            extra={"total_unique_domains": len(unique)},
        )
        return unique

    async def _import_csv_source(self, source_def: dict) -> List[str]:
        """Download and parse a CSV dataset.

        Args:
            source_def: Dict with ``url``, ``domain_col``, ``name_col`` keys.

        Returns:
            List of normalised apex domain strings.
        """
        domains: List[str] = []
        try:
            async with httpx.AsyncClient(
                timeout=_HTTP_TIMEOUT,
                headers={"User-Agent": "JobHunterBot/1.0"},
            ) as client:
                resp = await client.get(source_def["url"])
                if resp.status_code != 200:
                    logger.warning(
                        "CSV source unavailable",
                        extra={"source": source_def["name"], "status": resp.status_code},
                    )
                    return []
                content = resp.text
        except Exception as exc:
            logger.warning(
                "CSV source fetch failed",
                extra={"source": source_def["name"], "error": str(exc)},
            )
            return []

        reader = csv.DictReader(io.StringIO(content))
        domain_col = source_def.get("domain_col", "domain")
        for row in reader:
            raw = row.get(domain_col, "").strip()
            if not raw:
                continue
            apex = normalize_apex_domain(raw)
            if apex and not is_job_board(apex):
                domains.append(apex)

        return domains

    async def _import_startup_india(self) -> List[str]:
        """Import startup domains from the Startup India portal API.

        Returns:
            List of normalised apex domain strings.
        """
        domains: List[str] = []
        page = 0
        max_pages = 100  # safety cap

        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            headers={"User-Agent": "JobHunterBot/1.0"},
        ) as client:
            while page < max_pages:
                payload = {
                    "category": "startups",
                    "subCategory": "none",
                    "pageNo": page,
                    "pageSize": _STARTUP_INDIA_PAGE_SIZE,
                }
                try:
                    resp = await client.post(
                        _STARTUP_INDIA_API,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    if resp.status_code != 200:
                        logger.debug(
                            "Startup India API non-200",
                            extra={"page": page, "status": resp.status_code},
                        )
                        break

                    data = resp.json()
                    profiles = data.get("profiles") or data.get("data") or []
                    if not profiles:
                        break

                    for profile in profiles:
                        website = profile.get("website") or profile.get("websiteUrl") or ""
                        if website:
                            apex = normalize_apex_domain(website)
                            if apex and not is_job_board(apex):
                                domains.append(apex)

                    page += 1
                    await self.rate_limiter.wait("startup_india")

                except Exception as exc:
                    logger.warning(
                        "Startup India API error",
                        extra={"page": page, "error": str(exc)},
                    )
                    break

        return domains

    async def _import_msme_udyam(self) -> List[str]:
        """Import company website domains from the MSME UDYAM registered units
        bulk dataset on data.gov.in.

        Endpoint: GET /resource/{resource_id}?api-key=...&format=json&limit=...&offset=...
        Resource: List of MSME Registered Units under UDYAM

        Credentials and limits are read from config (DATAGOV_API_KEY,
        DATAGOV_MSME_RESOURCE_ID, DATAGOV_MSME_MAX_PAGES, DATAGOV_PAGE_SIZE).

        No scraping — pure paginated API download. No robots.txt concern.

        Returns:
            List of normalised apex domain strings.
        """
        api_key = config.datagov_api_key
        resource_id = config.datagov_msme_resource_id
        page_size = config.datagov_page_size
        max_pages = config.datagov_msme_max_pages

        if not api_key or not resource_id:
            logger.warning(
                "MSME UDYAM import skipped — DATAGOV_API_KEY or "
                "DATAGOV_MSME_RESOURCE_ID not set in config"
            )
            return []

        domains: List[str] = []
        offset = 0

        # Column name candidates for website/domain — the API field names
        # can vary between dataset versions; check all known variants.
        _WEBSITE_FIELDS = (
            "website", "Website", "website_url", "WebsiteUrl",
            "web", "url", "Url", "URL", "domain", "Domain",
        )

        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            headers={"User-Agent": "JobHunterBot/1.0"},
        ) as client:
            for _ in range(max_pages):
                params = {
                    "api-key": api_key,
                    "format": "json",
                    "limit": page_size,
                    "offset": offset,
                }
                try:
                    resp = await client.get(
                        f"{_DATAGOV_API_BASE}/{resource_id}",
                        params=params,
                    )
                    if resp.status_code != 200:
                        logger.debug(
                            "MSME UDYAM API non-200",
                            extra={"offset": offset, "status": resp.status_code},
                        )
                        break

                    data = resp.json()
                    records = data.get("records") or data.get("data") or []
                    if not records:
                        break

                    for record in records:
                        website = None
                        for field in _WEBSITE_FIELDS:
                            val = record.get(field, "")
                            if val and isinstance(val, str) and val.strip():
                                website = val.strip()
                                break

                        if not website:
                            continue

                        apex = normalize_apex_domain(website)
                        if apex and not is_job_board(apex):
                            domains.append(apex)

                    # Stop if fewer records than requested — end of dataset
                    if len(records) < page_size:
                        break

                    offset += page_size
                    await self.rate_limiter.wait("msme_udyam")

                except Exception as exc:
                    logger.warning(
                        "MSME UDYAM API error",
                        extra={"offset": offset, "error": str(exc)},
                    )
                    break

        logger.info(
            "MSME UDYAM import complete",
            extra={"domains_with_website": len(domains)},
        )
        return domains

    async def _import_mca21(self) -> List[str]:
        """Import company names from MCA21 via data.gov.in open API.

        Note: MCA21 records contain company names only, no domains.
        These are stored as ``name_only`` records for dedup cross-referencing.
        Returns an empty list here — name-only records are handled separately
        by the enrichment pipeline when a domain is discovered for the same name.

        Returns:
            Empty list (name-only records not returned as enrichable domains).
        """
        # MCA21 provides legal company names without domains.
        # Stored as name_only records — not returned for enrichment.
        logger.debug("MCA21 name-only import not returning domains (by design)")
        return []
