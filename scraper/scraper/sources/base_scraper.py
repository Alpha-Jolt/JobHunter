"""Abstract base class for all platform scrapers."""

from abc import ABC, abstractmethod
from typing import List

from scraper.core.rate_limiter import RateLimiter
from scraper.core.retry_handler import RetryHandler
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.logging_.logger import Logger


class BaseScraper(ABC):
    """All scrapers inherit from this class."""

    def __init__(
        self,
        rate_limiter: RateLimiter,
        retry_handler: RetryHandler,
        debug: bool = False,
    ) -> None:
        self.rate_limiter = rate_limiter
        self.retry_handler = retry_handler
        self.debug = debug
        self.logger = Logger.get_logger(self.__class__.__name__)

    @abstractmethod
    async def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        **kwargs,
    ) -> List[IntermediateJob]:
        """Scrape jobs for the given keywords and locations."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialise scraper resources (browser, HTTP session, etc.)."""

    @abstractmethod
    async def close(self) -> None:
        """Release all resources."""

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the canonical source identifier (e.g. 'indeed')."""

    async def __aenter__(self) -> "BaseScraper":
        await self.initialize()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()
