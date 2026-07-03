"""Enrichment pipeline — orchestrates all enrichment steps for a single domain."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Set

from scraper.sources.company_discovery.enrichment.ats_detector import (
    detect_ats_from_html,
)
from scraper.sources.company_discovery.enrichment.career_page_finder import (
    find_career_page,
)
from scraper.sources.company_discovery.enrichment.domain_utils import (
    build_dedup_fingerprint,
    is_job_board,
    normalize_apex_domain,
    normalize_company_name,
)
from scraper.sources.company_discovery.enrichment.email_extractor import (
    EmailExtractor,
)
from scraper.sources.company_discovery.enrichment.metadata_extractor import (
    MetadataExtractor,
)
from scraper.sources.company_discovery.enrichment.robots_checker import (
    RobotsChecker,
)

logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    """Orchestrates the full enrichment sequence for a single domain.

    Steps:
    1. Domain normalisation + job-board filter
    2. Queue-level dedup (in-memory known-domain set)
    3. robots.txt compliance check
    4. Career page discovery
    5. Email extraction and classification
    6. ATS detection
    7. Company metadata extraction
    8. CompanyRecord construction

    Args:
        robots_checker: Shared RobotsChecker instance for the session.
        email_extractor: Shared EmailExtractor instance.
        metadata_extractor: Shared MetadataExtractor instance.
        known_domains: Set of apex domains already in the companies table.
            Updated in-place as new companies are enriched.
    """

    def __init__(
        self,
        robots_checker: Optional[RobotsChecker] = None,
        email_extractor: Optional[EmailExtractor] = None,
        metadata_extractor: Optional[MetadataExtractor] = None,
        known_domains: Optional[Set[str]] = None,
    ) -> None:
        self._robots_checker = robots_checker or RobotsChecker()
        self._email_extractor = email_extractor or EmailExtractor()
        self._metadata_extractor = metadata_extractor or MetadataExtractor()
        self._known_domains: Set[str] = known_domains if known_domains is not None else set()

    async def enrich(
        self,
        raw_domain: str,
        source: str,
        source_detail: Optional[str] = None,
        company_name_hint: Optional[str] = None,
    ) -> Optional[dict]:
        """Run the full enrichment pipeline for a single domain.

        Args:
            raw_domain: Raw domain or URL string from a discovery source.
            source: Source tag for the companies table.
            source_detail: Optional detail about the specific source.
            company_name_hint: Optional company name from the discovery source.

        Returns:
            Dict of company fields ready to upsert, or None if the domain
            should be skipped (job board, already enriched, robots-blocked).
        """
        # Step 1 — Normalise domain
        apex_domain = normalize_apex_domain(raw_domain)
        if not apex_domain:
            logger.debug("Domain normalisation failed", extra={"raw": raw_domain})
            return None

        if is_job_board(apex_domain):
            logger.debug("Job board filtered", extra={"domain": apex_domain})
            return None

        # Step 2 — Queue-level dedup (in-memory)
        if apex_domain in self._known_domains:
            logger.debug("Domain already known — skipping", extra={"domain": apex_domain})
            return None

        logger.info("Enriching domain", extra={"domain": apex_domain})

        # Step 3 — robots.txt compliance
        robots_allowed = await self._robots_checker.is_domain_enrichable(apex_domain)
        if not robots_allowed:
            logger.info("robots.txt blocked enrichment", extra={"domain": apex_domain})
            normalized_name = normalize_company_name(company_name_hint or apex_domain)
            fingerprint = build_dedup_fingerprint(normalized_name, apex_domain)
            return {
                "company_id": uuid.uuid4(),
                "apex_domain": apex_domain,
                "normalized_name": normalized_name,
                "company_name": company_name_hint,
                "source": source,
                "source_detail": source_detail,
                "robots_txt_allowed": False,
                "crawl_status": "robots_blocked",
                "dedup_fingerprint": fingerprint,
                "discovery_date": datetime.now(timezone.utc),
                "subdomains": [],
                "career_emails": [],
                "contact_emails": [],
                "email_trust": "unverified",
                "ats_platform": "none",
            }

        # Step 4 — Career page discovery
        career_page_url = await find_career_page(apex_domain)

        # Step 5 — Email extraction
        email_data = await self._email_extractor.extract(apex_domain)
        career_emails: list = email_data.get("career_emails", [])
        contact_emails: list = email_data.get("contact_emails", [])

        # Determine overall email_trust
        all_emails = career_emails + contact_emails
        from scraper.sources.company_discovery.enrichment.email_classifier import classify_email
        has_low_trust = any(
            (result := classify_email(e)) and result[1] == "low_trust"
            for e in all_emails
        )
        email_trust = "low_trust" if has_low_trust else "unverified"

        # Step 6 — ATS detection (requires career page HTML)
        ats_platform = "none"
        if career_page_url:
            ats_platform = await self._detect_ats(career_page_url)

        # Step 7 — Company metadata
        meta = await self._metadata_extractor.extract(apex_domain)
        company_name = meta.get("company_name") or company_name_hint or apex_domain
        industry = meta.get("industry")
        hq_location = meta.get("hq_location")

        # Step 8 — Build record
        normalized_name = normalize_company_name(company_name)
        fingerprint = build_dedup_fingerprint(normalized_name, apex_domain)

        record = {
            "company_id": uuid.uuid4(),
            "company_name": company_name,
            "normalized_name": normalized_name,
            "apex_domain": apex_domain,
            "subdomains": [],
            "career_page_url": career_page_url,
            "career_emails": career_emails,
            "contact_emails": contact_emails,
            "email_trust": email_trust,
            "ats_platform": ats_platform,
            "industry": industry,
            "hq_location": hq_location,
            "company_size": None,
            "source": source,
            "source_detail": source_detail,
            "robots_txt_allowed": True,
            "discovery_date": datetime.now(timezone.utc),
            "last_enriched_at": datetime.now(timezone.utc),
            "email_last_crawled_at": datetime.now(timezone.utc),
            "crawl_status": "enriched",
            "dedup_fingerprint": fingerprint,
            "related_company_id": None,
        }

        # Mark as known so downstream queue skips it
        self._known_domains.add(apex_domain)

        logger.info(
            "Domain enriched",
            extra={
                "domain": apex_domain,
                "ats": ats_platform,
                "career_page": bool(career_page_url),
                "career_emails": len(career_emails),
            },
        )
        return record

    async def _detect_ats(self, career_page_url: str) -> str:
        """Fetch the career page HTML and detect ATS platform.

        Uses the static HTML fallback (no Playwright) to avoid overhead
        for platforms detectable from raw HTML.

        Args:
            career_page_url: Full URL of the career page.

        Returns:
            ATS platform key string.
        """
        import httpx

        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                follow_redirects=True,
                headers={"User-Agent": "JobHunterBot/1.0"},
            ) as client:
                resp = await client.get(career_page_url)
                if resp.status_code == 200:
                    return detect_ats_from_html(resp.text)
        except Exception as exc:
            logger.debug(
                "ATS detection fetch failed",
                extra={"url": career_page_url, "error": str(exc)},
            )
        return "none"
