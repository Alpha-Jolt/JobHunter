"""LinkedIn scraper stub — Phase 0 placeholder."""

from typing import List

from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.sources.base_scraper import BaseScraper


class LinkedInScraper(BaseScraper):
    """
    LinkedIn scraper stub (Phase 0).
    Full implementation deferred pending API partnership.
    """

    async def scrape(
        self, keywords: List[str], locations: List[str], **kwargs
    ) -> List[IntermediateJob]:
        self.logger.warning("LinkedIn scraping not implemented in Phase 0")
        return []

    async def initialize(self) -> None:
        pass

    async def close(self) -> None:
        pass

    def get_source_name(self) -> str:
        return "linkedin"
