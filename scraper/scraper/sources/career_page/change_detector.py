"""Change detector — compares content hashes to avoid re-processing unchanged jobs."""

import logging
from typing import Optional

from scraper.sources.career_page.url_utils import compute_content_hash

logger = logging.getLogger(__name__)


class ChangeDetector:
    """Detects whether a job's content has changed since the last crawl.

    Uses MD5(normalised_title + description) as the content fingerprint.
    When the hash matches the stored value, only last_seen_at is updated.
    """

    def compute_content_hash(self, job_title: str, description: str) -> str:
        """Compute the content hash for a job.

        Args:
            job_title: Job title string.
            description: Full job description text.

        Returns:
            32-character MD5 hex digest.
        """
        return compute_content_hash(job_title, description)

    def is_changed(self, stored_hash: Optional[str], new_hash: str) -> bool:
        """Return True if the content hash differs from the stored value.

        A None stored_hash means the job is new — always returns True.

        Args:
            stored_hash: Previously stored content hash, or None if new.
            new_hash: Freshly computed content hash.

        Returns:
            True if the content has changed or the job is new.
        """
        if stored_hash is None:
            return True
        changed = stored_hash != new_hash
        if changed:
            logger.debug(
                "Job content changed",
                extra={"stored": stored_hash, "new": new_hash},
            )
        return changed
