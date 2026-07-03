"""ATS public API extractor — Greenhouse, Lever, and Ashby free-tier APIs."""

import logging
from typing import List, Optional

import httpx

from scraper.sources.career_page.base import BaseCareerExtractor
from scraper.sources.company_discovery.enrichment.ats_detector import extract_ats_slug

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 15.0

# ATS public API endpoint templates — no auth required
_GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
_LEVER_API = "https://api.lever.co/v0/postings/{slug}?mode=json"
_ASHBY_GRAPHQL = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"

_ASHBY_QUERY = """
query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
  jobBoard: jobBoardWithTeams(
    organizationHostedJobsPageName: $organizationHostedJobsPageName
  ) {
    jobPostings {
      id
      title
      locationName
      employmentType
      descriptionHtml
      externalLink
      publishedAt
    }
  }
}
"""


class ATSApiExtractor(BaseCareerExtractor):
    """Extracts jobs via public ATS APIs for Greenhouse, Lever, and Ashby.

    Falls back gracefully to returning an empty list when the slug cannot be
    determined or the API returns a non-200 status.
    """

    def get_extraction_method(self) -> str:
        return "ats_api"

    async def extract(self, company: dict) -> List[dict]:
        """Try the appropriate ATS API based on the company's ats_platform.

        Args:
            company: Company record dict.

        Returns:
            List of raw job field dicts.
        """
        ats = company.get("ats_platform", "none")
        career_url = company.get("career_page_url", "") or ""
        slug = extract_ats_slug(ats, career_url)

        if not slug:
            logger.debug(
                "ATS slug not determinable — skipping API extraction",
                extra={"company": company.get("apex_domain"), "ats": ats},
            )
            return []

        if ats == "greenhouse":
            return await self._extract_greenhouse(slug, company)
        if ats == "lever":
            return await self._extract_lever(slug, company)
        if ats == "ashby":
            return await self._extract_ashby(slug, company)

        return []

    async def _extract_greenhouse(self, slug: str, company: dict) -> List[dict]:
        """Extract jobs from Greenhouse public board API.

        Args:
            slug: Company slug for the Greenhouse API.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        url = _GREENHOUSE_API.format(slug=slug)
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
                resp = await client.get(url, headers={"User-Agent": "JobHunterBot/1.0"})
        except Exception as exc:
            logger.debug("Greenhouse API request failed", extra={"error": str(exc)})
            return []

        if resp.status_code == 404:
            return []  # unknown slug — caller falls back to next extractor
        if resp.status_code != 200:
            logger.debug("Greenhouse API non-200", extra={"status": resp.status_code})
            return []

        data = resp.json()
        jobs = []
        for item in data.get("jobs", []):
            jobs.append({
                "job_title": item.get("title", ""),
                "job_url": item.get("absolute_url", ""),
                "description": _strip_html(item.get("content", "")),
                "location": _first_location(item.get("location")),
                "posted_at": item.get("updated_at"),
                "apply_url": item.get("absolute_url", ""),
                "ats_platform": "greenhouse",
                "extraction_method": "ats_api",
                "company_id": company.get("company_id"),
            })
        logger.info(
            "Greenhouse API extracted",
            extra={"slug": slug, "jobs": len(jobs)},
        )
        return jobs

    async def _extract_lever(self, slug: str, company: dict) -> List[dict]:
        """Extract jobs from Lever public postings API.

        Args:
            slug: Company slug for the Lever API.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        url = _LEVER_API.format(slug=slug)
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
                resp = await client.get(url, headers={"User-Agent": "JobHunterBot/1.0"})
        except Exception as exc:
            logger.debug("Lever API request failed", extra={"error": str(exc)})
            return []

        if resp.status_code == 404:
            return []
        if resp.status_code != 200:
            return []

        data = resp.json()
        # Lever returns a list of posting objects
        postings = data if isinstance(data, list) else data.get("data", [])
        jobs = []
        for item in postings:
            cats = item.get("categories", {})
            jobs.append({
                "job_title": item.get("text", ""),
                "job_url": item.get("hostedUrl", ""),
                "description": _strip_html(item.get("descriptionHtml") or item.get("description", "")),
                "location": cats.get("location", ""),
                "job_type": _map_lever_commitment(cats.get("commitment", "")),
                "posted_at": _ms_to_iso(item.get("createdAt")),
                "apply_url": item.get("applyUrl", ""),
                "ats_platform": "lever",
                "extraction_method": "ats_api",
                "company_id": company.get("company_id"),
            })
        logger.info(
            "Lever API extracted",
            extra={"slug": slug, "jobs": len(jobs)},
        )
        return jobs

    async def _extract_ashby(self, slug: str, company: dict) -> List[dict]:
        """Extract jobs from Ashby GraphQL API.

        Args:
            slug: Ashby organisation slug.
            company: Company record dict.

        Returns:
            List of raw job dicts.
        """
        payload = {
            "operationName": "ApiJobBoardWithTeams",
            "variables": {"organizationHostedJobsPageName": slug},
            "query": _ASHBY_QUERY,
        }
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
                resp = await client.post(
                    _ASHBY_GRAPHQL,
                    json=payload,
                    headers={
                        "User-Agent": "JobHunterBot/1.0",
                        "Content-Type": "application/json",
                    },
                )
        except Exception as exc:
            logger.debug("Ashby API request failed", extra={"error": str(exc)})
            return []

        if resp.status_code != 200:
            return []

        data = resp.json()
        postings = (
            data.get("data", {}).get("jobBoard", {}).get("jobPostings", []) or []
        )
        jobs = []
        for item in postings:
            jobs.append({
                "job_title": item.get("title", ""),
                "job_url": item.get("externalLink", ""),
                "description": _strip_html(item.get("descriptionHtml", "")),
                "location": item.get("locationName", ""),
                "job_type": _map_ashby_employment(item.get("employmentType", "")),
                "posted_at": item.get("publishedAt"),
                "apply_url": item.get("externalLink", ""),
                "ats_platform": "ashby",
                "extraction_method": "ats_api",
                "company_id": company.get("company_id"),
            })
        logger.info(
            "Ashby API extracted",
            extra={"slug": slug, "jobs": len(jobs)},
        )
        return jobs


# --- Helpers ----------------------------------------------------------------

def _strip_html(html: Optional[str]) -> str:
    """Remove HTML tags from a string."""
    if not html:
        return ""
    import re
    return re.sub(r"<[^>]+>", " ", html).strip()


def _first_location(location_obj: object) -> str:
    """Extract a location string from a Greenhouse location object."""
    if isinstance(location_obj, dict):
        return location_obj.get("name", "")
    if isinstance(location_obj, str):
        return location_obj
    return ""


def _ms_to_iso(ms_timestamp: Optional[int]) -> Optional[str]:
    """Convert a millisecond Unix timestamp to ISO 8601 string."""
    if not ms_timestamp:
        return None
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).isoformat()


def _map_lever_commitment(commitment: str) -> str:
    """Map Lever commitment strings to canonical job_type values."""
    mapping = {
        "full-time": "fulltime",
        "part-time": "parttime",
        "contract": "contract",
        "internship": "internship",
        "freelance": "freelance",
    }
    return mapping.get(commitment.lower(), "fulltime")


def _map_ashby_employment(employment_type: str) -> str:
    """Map Ashby employment type strings to canonical job_type values."""
    mapping = {
        "FullTime": "fulltime",
        "PartTime": "parttime",
        "Contract": "contract",
        "Intern": "internship",
        "Freelance": "freelance",
    }
    return mapping.get(employment_type, "fulltime")
