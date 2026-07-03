"""Integration tests for the career page router — strategy routing and cascade."""

import pytest
import respx
import httpx

from scraper.sources.career_page.router import CareerPageRouter


_COMPANY_GREENHOUSE = {
    "company_id": "uuid-acme",
    "apex_domain": "acme.com",
    "career_page_url": "https://boards.greenhouse.io/acmecorp",
    "ats_platform": "greenhouse",
    "career_emails": ["careers@acme.com"],
    "company_name": "Acme Corp",
}

_COMPANY_CUSTOM = {
    "company_id": "uuid-beta",
    "apex_domain": "beta.com",
    "career_page_url": "https://beta.com/careers",
    "ats_platform": "custom",
    "career_emails": [],
    "company_name": "Beta Co",
}

_GREENHOUSE_RESPONSE = {
    "jobs": [
        {
            "title": "Python Engineer",
            "absolute_url": "https://boards.greenhouse.io/acmecorp/jobs/1",
            "content": "We need Python skills.",
            "location": {"name": "Bangalore"},
            "updated_at": "2026-07-01T00:00:00Z",
        }
    ]
}

_JSON_LD_HTML = """
<html><head>
<script type="application/ld+json">
{"@type": "JobPosting", "title": "React Developer",
 "url": "https://beta.com/careers/jobs/1",
 "description": "React and TypeScript required."}
</script>
</head></html>
"""


@pytest.mark.asyncio
class TestCareerPageRouter:
    async def test_uses_greenhouse_api_for_greenhouse_company(self):
        router = CareerPageRouter()

        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(404)
            )
            respx.get(
                "https://boards-api.greenhouse.io/v1/boards/acmecorp/jobs?content=true"
            ).mock(return_value=httpx.Response(200, json=_GREENHOUSE_RESPONSE))

            jobs = await router.extract_jobs(_COMPANY_GREENHOUSE)

        assert len(jobs) == 1
        assert jobs[0]["job_title"] == "Python Engineer"
        assert jobs[0]["extraction_method"] == "ats_api"
        assert jobs[0]["source_channel"] == "career_page"

    async def test_falls_back_to_json_ld_for_custom_ats(self):
        router = CareerPageRouter()

        with respx.mock:
            respx.get("https://beta.com/robots.txt").mock(
                return_value=httpx.Response(404)
            )
            respx.get("https://beta.com/careers").mock(
                return_value=httpx.Response(200, text=_JSON_LD_HTML)
            )

            jobs = await router.extract_jobs(_COMPANY_CUSTOM)

        assert len(jobs) == 1
        assert jobs[0]["job_title"] == "React Developer"
        assert jobs[0]["extraction_method"] == "json_ld"

    async def test_robots_blocked_returns_empty(self):
        router = CareerPageRouter()

        with respx.mock:
            respx.get("https://beta.com/robots.txt").mock(
                return_value=httpx.Response(
                    200, text="User-agent: *\nDisallow: /careers"
                )
            )

            jobs = await router.extract_jobs(_COMPANY_CUSTOM)

        assert jobs == []

    async def test_no_career_page_returns_empty(self):
        router = CareerPageRouter()
        company = dict(_COMPANY_CUSTOM)
        company["career_page_url"] = None

        jobs = await router.extract_jobs(company)
        assert jobs == []

    def test_mark_closed_jobs(self):
        router = CareerPageRouter()
        existing = {"hash1", "hash2", "hash3"}
        seen = {"hash1", "hash3"}
        closed = router.mark_closed_jobs(existing, seen)
        assert closed == {"hash2"}

    def test_mark_closed_jobs_all_seen(self):
        router = CareerPageRouter()
        existing = {"hash1", "hash2"}
        seen = {"hash1", "hash2"}
        closed = router.mark_closed_jobs(existing, seen)
        assert closed == set()

    async def test_enriched_job_has_required_metadata_fields(self):
        router = CareerPageRouter()

        with respx.mock:
            respx.get("https://acme.com/robots.txt").mock(
                return_value=httpx.Response(404)
            )
            respx.get(
                "https://boards-api.greenhouse.io/v1/boards/acmecorp/jobs?content=true"
            ).mock(return_value=httpx.Response(200, json=_GREENHOUSE_RESPONSE))

            jobs = await router.extract_jobs(_COMPANY_GREENHOUSE)

        assert len(jobs) == 1
        job = jobs[0]
        assert "career_job_id" in job
        assert "url_hash" in job
        assert "content_hash" in job
        assert "scraped_at" in job
        assert "last_seen_at" in job
        assert job["status"] == "raw"
        assert job["source_channel"] == "career_page"
        assert job.get("apply_email") == "careers@acme.com"
