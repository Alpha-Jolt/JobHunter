"""Output adapter for api_sourced_jobs table."""

import json
from typing import List

from scraper.db.connection import get_db_session
from scraper.db.models import ApiSourcedJob
from scraper.extraction.intermediate_schema import IntermediateJob


class ApiJobsOutputAdapter:
    """Inserts IntermediateJobs into the api_sourced_jobs table."""

    async def save_jobs(self, jobs: List[IntermediateJob]) -> int:
        if not jobs:
            return 0

        inserted_count = 0
        async for session in get_db_session():
            for job in jobs:
                # Basic dedup based on (source, external_id)
                stmt = """
                    INSERT INTO api_sourced_jobs (
                        source, source_actor_id, external_id, title, company_name,
                        company_domain, location, description, apply_url, apply_email,
                        extra_data, status
                    ) VALUES (
                        :source, :source_actor_id, :external_id, :title, :company_name,
                        :company_domain, :location, :description, :apply_url, :apply_email,
                        :extra_data, :status
                    ) ON CONFLICT (source, external_id) DO UPDATE SET
                        last_seen_at = CURRENT_TIMESTAMP,
                        extra_data = api_sourced_jobs.extra_data || :extra_data
                    RETURNING job_id;
                """
                extra_data = json.dumps(job.extra_raw or {})
                
                from sqlalchemy import text
                try:
                    await session.execute(
                        text(stmt),
                        {
                            "source": job.source.split("/")[0] if "/" in job.source else job.source,
                            "source_actor_id": job.source,
                            "external_id": job.external_id,
                            "title": job.title,
                            "company_name": job.company_name,
                            "company_domain": job.company_domain,
                            "location": job.location_raw,
                            "description": job.description,
                            "apply_url": job.raw_url,
                            "apply_email": job.apply_email_raw,
                            "extra_data": extra_data,
                            "status": "raw"
                        }
                    )
                    inserted_count += 1
                except Exception as e:
                    # In a real app we'd log this properly
                    print(f"Error inserting API sourced job {job.external_id}: {e}")
                    
            await session.commit()
            
        return inserted_count
