"""JSON-LD structured data extractor — Schema.org JobPosting."""

import json
import logging
import re
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from scraper.sources.career_page.base import BaseCareerExtractor

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 15.0

_EMPLOYMENT_TYPE_MAP = {
    "FULL_TIME": "fulltime",
    "PART_TIME": "parttime",
    "CONTRACTOR": "contract",
    "TEMPORARY": "contract",
    "INTERN": "internship",
    "VOLUNTEER": "freelance",
    "PER_DIEM": "freelance",
    "OTHER": "fulltime",
}


class JSONLDExtractor(BaseCareerExtractor):
    """Extracts job listings from Schema.org JobPosting JSON-LD blocks.

    Handles:
    - Single JobPosting on an individual job detail page
    - Multiple JobPostings listed inline on a career page
    - ItemList wrapping multiple JobPosting entries
    """

    def get_extraction_method(self) -> str:
        return "json_ld"

    async def extract(self, company: dict) -> List[dict]:
        """Fetch the career page and extract all JSON-LD job postings.

        Args:
            company: Company record dict.

        Returns:
            List of raw job field dicts.
        """
        career_url = company.get("career_page_url")
        if not career_url:
            return []

        html = await self._fetch(career_url)
        if not html:
            return []

        jobs = self._parse_json_ld(html, company)
        logger.info(
            "JSON-LD extracted",
            extra={"url": career_url, "jobs": len(jobs)},
        )
        return jobs

    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return HTML text.

        Args:
            url: URL to fetch.

        Returns:
            HTML string or None on failure.
        """
        try:
            async with httpx.AsyncClient(
                timeout=_HTTP_TIMEOUT,
                follow_redirects=True,
                headers={"User-Agent": "JobHunterBot/1.0"},
            ) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text
        except Exception as exc:
            logger.debug("JSON-LD fetch failed", extra={"url": url, "error": str(exc)})
        return None

    def _parse_json_ld(self, html: str, company: dict) -> List[dict]:
        """Parse all JSON-LD JobPosting nodes from an HTML page.

        Args:
            html: Raw HTML string.
            company: Company record dict.

        Returns:
            List of raw job field dicts.
        """
        soup = BeautifulSoup(html, "lxml")
        jobs: List[dict] = []

        for script_tag in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script_tag.string or "")
            except Exception:
                continue

            nodes = data if isinstance(data, list) else [data]
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                node_type = node.get("@type", "")
                types = node_type if isinstance(node_type, list) else [node_type]

                if "JobPosting" in types:
                    job = self._map_job_posting(node, company)
                    if job:
                        jobs.append(job)

                elif "ItemList" in types:
                    for list_item in node.get("itemListElement", []):
                        if isinstance(list_item, dict):
                            item = list_item.get("item", list_item)
                            if isinstance(item, dict) and "JobPosting" in str(item.get("@type", "")):
                                job = self._map_job_posting(item, company)
                                if job:
                                    jobs.append(job)

        return jobs

    def _map_job_posting(self, node: dict, company: dict) -> Optional[dict]:
        """Map a Schema.org JobPosting node to a raw job field dict.

        Args:
            node: JSON-LD JobPosting dict.
            company: Company record dict.

        Returns:
            Raw job dict, or None if the title is missing.
        """
        title = _clean_text(node.get("title") or node.get("name", ""))
        if not title:
            return None

        job_url = node.get("url") or node.get("@id") or company.get("career_page_url", "")
        description = _strip_html(node.get("description", ""))

        # Location
        location = ""
        loc_obj = node.get("jobLocation")
        if isinstance(loc_obj, dict):
            address = loc_obj.get("address", {})
            if isinstance(address, dict):
                location = address.get("addressLocality", "")
            elif isinstance(address, str):
                location = address
        elif isinstance(loc_obj, str):
            location = loc_obj

        # Remote type
        remote_type = None
        job_location_type = str(node.get("jobLocationType", "")).lower()
        if "remote" in job_location_type:
            remote_type = "remote"
        elif "hybrid" in job_location_type:
            remote_type = "hybrid"

        # Salary
        salary_min, salary_max = None, None
        base_salary = node.get("baseSalary", {})
        if isinstance(base_salary, dict):
            value = base_salary.get("value", {})
            if isinstance(value, dict):
                salary_min = _to_int(value.get("minValue"))
                salary_max = _to_int(value.get("maxValue"))

        # Employment type
        emp_type = node.get("employmentType", "")
        if isinstance(emp_type, list):
            emp_type = emp_type[0] if emp_type else ""
        job_type = _EMPLOYMENT_TYPE_MAP.get(emp_type.upper(), "fulltime")

        return {
            "job_title": title,
            "job_url": job_url,
            "description": description,
            "location": location,
            "remote_type": remote_type,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "job_type": job_type,
            "posted_at": node.get("datePosted"),
            "apply_url": node.get("url") or job_url,
            "ats_platform": company.get("ats_platform", "custom"),
            "extraction_method": "json_ld",
            "company_id": company.get("company_id"),
        }


# --- Helpers ----------------------------------------------------------------

def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).strip()


def _to_int(value: object) -> Optional[int]:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None
