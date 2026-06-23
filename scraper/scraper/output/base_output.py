"""Abstract output interface."""

from abc import ABC, abstractmethod
from typing import List

from scraper.normalization.canonical_schema import CanonicalJob


class BaseOutput(ABC):
    """All output adapters implement this interface."""

    @abstractmethod
    async def write(self, jobs: List[CanonicalJob]) -> None:
        """Persist jobs to the output destination."""

    @abstractmethod
    async def read(self) -> List[CanonicalJob]:
        """Read jobs back from the output destination."""
