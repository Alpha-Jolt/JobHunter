"""Candidate email generator — produces HR-prefix emails for domains with no scraped emails.

Only runs post-enrichment when EmailExtractor found nothing. All generated
addresses are tagged low_trust and marked is_generated=True on the company record.
MX lookup gates generation — domains with no MX record are discarded entirely.
"""

import asyncio
import logging
from typing import List

import dns.exception
import dns.resolver

from scraper.config import config
from scraper.sources.company_discovery.enrichment.email_classifier import is_valid_email

logger = logging.getLogger(__name__)

# HR-signal prefixes to attempt for each qualifying domain.
# Order matters — prefixes tried first are more likely to be real HR addresses.
CANDIDATE_PREFIXES: List[str] = [
    "careers",
    "hr",
    "jobs",
    "recruitment",
    "talent",
    "hiring",
    "career",
    "job",
    "support",
]


class CandidateEmailGenerator:
    """Generates candidate HR email addresses for domains that have no scraped emails.

    Flow:
    1. MX lookup — if domain has no MX record, return empty list immediately.
    2. Build ``{prefix}@{apex_domain}`` for each prefix in CANDIDATE_PREFIXES.
    3. Validate format with is_valid_email().
    4. Return deduplicated list.

    All returned addresses are low_trust by definition — they are generated
    from a pattern, not extracted from page content. Callers must set
    is_generated=True on the company record when this method returns non-empty.

    Args:
        mx_timeout: DNS resolver timeout in seconds. Controlled via
            CANDIDATE_EMAIL_MX_TIMEOUT env var (default 5s).
    """

    def __init__(self, mx_timeout: float | None = None) -> None:
        self._mx_timeout = (
            mx_timeout if mx_timeout is not None
            else config.candidate_email_mx_timeout
        )

    async def generate(self, apex_domain: str) -> List[str]:
        """Return candidate email addresses for a domain, or empty list.

        Args:
            apex_domain: Normalised apex domain string (e.g. ``acme.co.in``).

        Returns:
            List of ``{prefix}@{apex_domain}`` strings that passed MX check,
            or empty list if MX lookup failed or domain is invalid.
        """
        if not apex_domain or "." not in apex_domain:
            return []

        has_mx = await self._check_mx(apex_domain)
        if not has_mx:
            logger.debug(
                "MX lookup failed — skipping candidate generation",
                extra={"domain": apex_domain},
            )
            return []

        candidates: List[str] = []
        seen: set = set()
        for prefix in CANDIDATE_PREFIXES:
            email = f"{prefix}@{apex_domain}".lower()
            if email not in seen and is_valid_email(email):
                seen.add(email)
                candidates.append(email)

        logger.debug(
            "Candidate emails generated",
            extra={"domain": apex_domain, "count": len(candidates)},
        )
        return candidates

    async def _check_mx(self, domain: str) -> bool:
        """Return True if the domain has at least one MX record.

        Uses asyncio executor to avoid blocking the event loop since
        dnspython's resolver is synchronous.

        Args:
            domain: Apex domain string.

        Returns:
            True if MX record found, False on any failure.
        """
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                None, self._resolve_mx, domain
            )
        except Exception as exc:
            logger.debug(
                "MX executor error",
                extra={"domain": domain, "error": str(exc)},
            )
            return False

    def _resolve_mx(self, domain: str) -> bool:
        """Synchronous MX resolution — runs in executor thread.

        Args:
            domain: Apex domain string.

        Returns:
            True if at least one MX record found.
        """
        resolver = dns.resolver.Resolver()
        resolver.timeout = self._mx_timeout
        resolver.lifetime = self._mx_timeout
        try:
            answers = resolver.resolve(domain, "MX")
            return len(answers) > 0
        except dns.resolver.NXDOMAIN:
            logger.debug("MX NXDOMAIN", extra={"domain": domain})
            return False
        except dns.resolver.NoAnswer:
            logger.debug("MX NoAnswer", extra={"domain": domain})
            return False
        except dns.exception.Timeout:
            logger.warning("MX timeout", extra={"domain": domain})
            return False
        except dns.exception.DNSException as exc:
            logger.debug(
                "MX DNS error",
                extra={"domain": domain, "error": str(exc)},
            )
            return False
