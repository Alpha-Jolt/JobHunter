"""Abstract base class for all career page job extractors."""

from abc import ABC, abstractmethod
from typing import List


class BaseCareerExtractor(ABC):
    """All career page extractors inherit from this class.

    Each extractor is responsible for extracting job listings from a company's
    career page using a specific strategy. Returns a list of raw job dicts
    that the router then passes through the job cleaner pipeline.
    """

    @abstractmethod
    async def extract(self, company: dict) -> List[dict]:
        """Extract job listings for the given company.

        Args:
            company: Company record dict with keys: apex_domain,
                career_page_url, ats_platform, company_id, company_name.

        Returns:
            List of raw job field dicts. Empty list if extraction fails
            or no jobs found.
        """

    @abstractmethod
    def get_extraction_method(self) -> str:
        """Return the extraction_method tag written to career_jobs table.

        Returns:
            One of: ats_api, json_ld, sitemap, api_reverse,
            html_parse, playwright_render.
        """
