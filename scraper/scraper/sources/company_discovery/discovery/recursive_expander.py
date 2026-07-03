"""Recursive expander stub — post-alpha feature, not active pre-alpha."""

import logging
import uuid
from typing import List

from scraper.sources.company_discovery.base import BaseCompanySource

logger = logging.getLogger(__name__)


class RecursiveExpander(BaseCompanySource):
    """Post-alpha stub — discovers domains from partner/customer/integration pages.

    This class is a stub and returns an empty list on every call.
    It is activated after the 1,000-company alpha target is reached.

    When active, it will crawl pages labelled:
    Partners, Customers, Clients, Case Studies, Integrations,
    Sponsors, and Technology Partners — extracting outbound domain links
    to feed back into the enrichment queue.
    """

    def get_source_tag(self) -> str:
        return "recursive"

    async def discover(
        self,
        company_id: uuid.UUID = None,
        career_page_url: str = None,
        **kwargs,
    ) -> List[str]:
        """Stub: log the call and return empty list.

        Args:
            company_id: UUID of the company whose pages would be crawled.
            career_page_url: Career page URL (not used in stub).

        Returns:
            Empty list — stub is not active pre-alpha.
        """
        logger.info(
            "RecursiveExpander stub called — not active pre-alpha",
            extra={
                "company_id": str(company_id) if company_id else None,
                "career_page_url": career_page_url,
            },
        )
        return []
