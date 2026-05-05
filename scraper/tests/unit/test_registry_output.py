"""Unit tests for RegistryOutput adapter."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from scraper.normalization.canonical_schema import CanonicalJob
from scraper.output.registry_output import RegistryOutput, _to_job_record


def _make_canonical(**kwargs) -> CanonicalJob:
    defaults = dict(
        source="naukri",
        external_id="ext-1",
        source_url="https://naukri.com/job/1",
        title="Python Developer",
        company_name="Acme",
        description="Build APIs with Python and Django." * 10,
        scraped_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return CanonicalJob(**defaults)


def test_to_job_record_maps_fields():
    job = _make_canonical(
        source="naukri",
        location_city="Bangalore",
        location_state="Karnataka",
        remote_type="hybrid",
        job_type="contract",
        salary_min=500000,
        salary_max=800000,
        experience_min=2,
        experience_max=5,
        skills_required=["Python", "Django"],
    )
    record = _to_job_record(job)

    assert record.source == "naukri"
    assert record.external_id == "ext-1"
    assert record.location == "Bangalore, Karnataka"
    assert record.remote_type == "hybrid"
    assert record.job_type == "contract"
    assert record.salary_min == 500000.0
    assert record.salary_max == 800000.0
    assert isinstance(record.job_id, uuid.UUID)


def test_to_job_record_unknown_remote_becomes_none():
    record = _to_job_record(_make_canonical(remote_type="unknown"))
    assert record.remote_type is None


def test_to_job_record_unknown_job_type_defaults_to_fulltime():
    record = _to_job_record(_make_canonical(job_type="unknown"))
    assert record.job_type == "fulltime"


def test_to_job_record_raises_for_unsupported_source():
    with pytest.raises(ValueError, match="Unsupported source"):
        _to_job_record(_make_canonical(source="mock"))


@pytest.mark.asyncio
async def test_registry_output_write_calls_save():
    registry = MagicMock()
    registry.save = AsyncMock()
    output = RegistryOutput(registry)

    jobs = [_make_canonical(external_id=f"ext-{i}") for i in range(3)]
    await output.write(jobs)

    registry.save.assert_called_once()
    saved = registry.save.call_args[0][0]
    assert len(saved) == 3


@pytest.mark.asyncio
async def test_registry_output_skips_unsupported_source():
    registry = MagicMock()
    registry.save = AsyncMock()
    output = RegistryOutput(registry)

    jobs = [_make_canonical(source="mock")]
    await output.write(jobs)

    registry.save.assert_not_called()


@pytest.mark.asyncio
async def test_registry_output_read_raises():
    output = RegistryOutput(MagicMock())
    with pytest.raises(NotImplementedError):
        await output.read()
