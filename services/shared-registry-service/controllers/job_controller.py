"""Translate JobRecord ↔ JobResponse."""

from models.schemas import JobResponse


def job_to_response(job) -> JobResponse:
    d = job.to_dict()
    return JobResponse(
        job_id=d["job_id"],
        source=d["source"],
        external_id=d["external_id"],
        title=d["title"],
        company_name=d["company_name"],
        company_domain=d.get("company_domain"),
        location=d.get("location"),
        remote_type=d.get("remote_type"),
        salary_min=d.get("salary_min"),
        salary_max=d.get("salary_max"),
        experience_min=d.get("experience_min"),
        experience_max=d.get("experience_max"),
        description=d["description"],
        skills_required=d.get("skills_required") or [],
        job_type=d["job_type"],
        apply_email=d.get("apply_email"),
        email_trust=d["email_trust"],
        apply_url=d.get("apply_url"),
        posted_at=d.get("posted_at"),
        scraped_at=d.get("scraped_at"),
        last_seen_at=d.get("last_seen_at"),
        status=d["status"],
    )
