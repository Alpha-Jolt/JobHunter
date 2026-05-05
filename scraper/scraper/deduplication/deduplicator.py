"""Hash-based deduplication across content, URL, and source ID."""

from typing import Dict, List, Set, Tuple

from scraper.normalization.canonical_schema import CanonicalJob


class Deduplicator:
    """Remove duplicate CanonicalJob entries using three strategies."""

    def __init__(self) -> None:
        self._seen_content: Set[str] = set()
        self._seen_urls: Set[str] = set()
        self._seen_source_ids: Set[Tuple[str, str]] = set()

    def deduplicate(
        self,
        jobs: List[CanonicalJob],
    ) -> Tuple[List[CanonicalJob], Dict[str, int]]:
        """
        Remove duplicates and return (unique_jobs, report).

        Report keys: total, unique, dup_by_content, dup_by_url, dup_by_id.
        """
        unique: List[CanonicalJob] = []
        report = {
            "total": len(jobs),
            "unique": 0,
            "dup_by_content": 0,
            "dup_by_url": 0,
            "dup_by_id": 0,
        }

        for job in jobs:
            is_dup, reason = self.is_duplicate(job)
            if is_dup:
                report[f"dup_by_{reason}"] = report.get(f"dup_by_{reason}", 0) + 1
            else:
                self._register(job)
                unique.append(job)

        report["unique"] = len(unique)
        return unique, report

    def is_duplicate(self, job: CanonicalJob) -> Tuple[bool, str]:
        """Return (True, reason) if duplicate, else (False, '')."""
        if job.content_hash and job.content_hash in self._seen_content:
            return True, "content"
        if job.url_hash and job.url_hash in self._seen_urls:
            return True, "url"
        sid = (job.source, job.external_id)
        if sid in self._seen_source_ids:
            return True, "id"
        return False, ""

    def _register(self, job: CanonicalJob) -> None:
        if job.content_hash:
            self._seen_content.add(job.content_hash)
        if job.url_hash:
            self._seen_urls.add(job.url_hash)
        self._seen_source_ids.add((job.source, job.external_id))

    def reset(self) -> None:
        """Clear all seen sets (use between independent pipeline runs)."""
        self._seen_content.clear()
        self._seen_urls.clear()
        self._seen_source_ids.clear()
