"""API reader — fetches raw JobRecords from the Orchestration API."""

from __future__ import annotations

import httpx
from datetime import datetime

from ai_engine.core.logging_.logger import get_logger
from ai_engine.features.ingestion.models.job_record import JobRecord
from ai_engine.core.config import get_settings

logger = get_logger(__name__)


def read_api() -> list[JobRecord]:
    """Fetch raw jobs from the Orchestration API.

    Returns:
        List of JobRecord instances with status 'raw'.
    """
    settings = get_settings()
    api_url = f"{settings.orchestration_api_url.rstrip('/')}/api/ai/jobs/raw"

    records: list[JobRecord] = []
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(api_url)
            response.raise_for_status()
            data = response.json()
            
        jobs_data = data.get("jobs", [])
        
        for job_dict in jobs_data:
            try:
                # Convert string timestamps back to datetime if necessary
                posted_at = job_dict.get("posted_at")
                if posted_at and isinstance(posted_at, str):
                    posted_at = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
                    
                scraped_at = job_dict.get("scraped_at")
                if scraped_at and isinstance(scraped_at, str):
                    scraped_at = datetime.fromisoformat(scraped_at.replace("Z", "+00:00"))
                
                records.append(JobRecord(
                    job_id=str(job_dict.get("job_id", "")),
                    source=job_dict.get("source", ""),
                    title=job_dict.get("title", ""),
                    company=job_dict.get("company_name", ""),
                    location=job_dict.get("location") or "",
                    remote_type=job_dict.get("remote_type") or "",
                    description=job_dict.get("description", ""),
                    skills_required=job_dict.get("skills_required", []),
                    apply_email=job_dict.get("apply_email") or "",
                    apply_url=job_dict.get("apply_url") or "",
                    posted_at=posted_at,
                    scraped_at=scraped_at,
                ))
            except Exception as exc:
                logger.warning("api_reader.skipped", job_id=job_dict.get("job_id"), error=str(exc))
                
    except Exception as exc:
        logger.error("api_reader.request_failed", url=api_url, error=str(exc))
        return []

    logger.info("api_reader.complete", loaded=len(records))
    return records
