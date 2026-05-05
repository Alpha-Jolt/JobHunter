"""Unit tests for Deduplicator."""

import pytest

from scraper.deduplication.deduplicator import Deduplicator
from scraper.normalization.canonical_schema import CanonicalJob


def _make_job(external_id: str, content_hash: str = "", url_hash: str = "") -> CanonicalJob:
    return CanonicalJob(
        source="naukri",
        external_id=external_id,
        source_url=f"https://naukri.com/job/{external_id}",
        title="Python Developer",
        company_name="Acme",
        description="Test description",
        content_hash=content_hash or f"hash_{external_id}",
        url_hash=url_hash or f"url_{external_id}",
    )


def test_unique_jobs_pass_through():
    dedup = Deduplicator()
    jobs = [_make_job("1"), _make_job("2"), _make_job("3")]
    unique, report = dedup.deduplicate(jobs)
    assert len(unique) == 3
    assert report["unique"] == 3


def test_duplicate_by_source_id():
    dedup = Deduplicator()
    j1 = _make_job("1", content_hash="hash_a", url_hash="url_a")
    j2 = _make_job("1", content_hash="hash_b", url_hash="url_b")
    unique, report = dedup.deduplicate([j1, j2])
    assert len(unique) == 1
    assert report["dup_by_id"] == 1


def test_duplicate_by_content_hash():
    dedup = Deduplicator()
    j1 = _make_job("1", content_hash="same_hash")
    j2 = _make_job("2", content_hash="same_hash")
    unique, report = dedup.deduplicate([j1, j2])
    assert len(unique) == 1
    assert report["dup_by_content"] == 1


def test_duplicate_by_url_hash():
    dedup = Deduplicator()
    j1 = _make_job("1", url_hash="same_url")
    j2 = _make_job("2", url_hash="same_url")
    unique, report = dedup.deduplicate([j1, j2])
    assert len(unique) == 1


def test_reset_clears_state():
    dedup = Deduplicator()
    jobs = [_make_job("1")]
    dedup.deduplicate(jobs)
    dedup.reset()
    unique, _ = dedup.deduplicate(jobs)
    assert len(unique) == 1
