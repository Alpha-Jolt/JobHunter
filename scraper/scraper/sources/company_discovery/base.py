"""Abstract base class for all company discovery sources."""

from abc import ABC, abstractmethod
from typing import List

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.logging_.logger import Logger


class BaseCompanySource(ABC):
    """All company discovery sources inherit from this class.

    Each source is responsible for returning a list of apex domains
    to be enqueued for enrichment. No enrichment logic lives here.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter,
        retry_handler: RetryHandler,
    ) -> None:
        self.rate_limiter = rate_limiter
        self.retry_handler = retry_handler
        self.logger = Logger.get_logger(self.__class__.__name__)

    @abstractmethod
    async def discover(self, **kwargs) -> List[str]:
        """Return a list of apex domains to enqueue for enrichment.

        Args:
            **kwargs: Source-specific parameters (e.g. role, location).

        Returns:
            List of normalised apex domain strings.
        """

    @abstractmethod
    def get_source_tag(self) -> str:
        """Return the source tag string written to companies.source column.

        Returns:
            One of: bootstrap_dataset, govt_registry, vc_portfolio,
            github_org, directory, search_discovery, recursive.
        """
