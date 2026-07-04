"""Company discovery and career jobs run management service.

Mirrors admin_api/scraper/service.py pattern:
- Creates ScraperAuditLog records (hash-chain audit trail).
- Pushes tasks directly to the Redis scraper:tasks queue.
- Provides Redis-first status lookup.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from scraper.models import ScraperAuditLog
from company_discovery.models import Company, CareerJob


def _generate_audit_hash(prev_hash: str, payload_str: str) -> str:
    """Compute SHA-256 audit hash chained from the previous entry."""
    combined = f"{prev_hash}|{payload_str}"
    return hashlib.sha256(combined.encode()).hexdigest()


async def create_run_and_enqueue(
    db: AsyncSession,
    r: redis.Redis,
    task_type: str,
    source: str,
    payload: dict,
) -> str:
    """Create an audit log record and push the task to Redis.

    Args:
        db: Async SQLAlchemy session.
        r: Redis async client.
        task_type: One of "search_discovery", "company_discovery_bootstrap",
                   "career_page_scrape".
        source: Human-readable source label for the audit log payload.
        payload: Full task payload forwarded to the scraper worker.

    Returns:
        run_id (UUID string) that callers can poll for status.
    """
    result = await db.execute(
        select(ScraperAuditLog).order_by(ScraperAuditLog.id.desc()).limit(1)
    )
    last_log = result.scalars().first()
    prev_hash = last_log.audit_hash if last_log else "genesis"

    run_id = str(uuid.uuid4())
    audit_payload = {"type": task_type, "source": source, **payload}
    payload_str = json.dumps(audit_payload, sort_keys=True)
    audit_hash = _generate_audit_hash(prev_hash, payload_str)

    audit_log = ScraperAuditLog(
        task_id=run_id,
        user_id="admin",
        request_id=str(uuid.uuid4()),
        audit_hash=audit_hash,
        payload=audit_payload,
    )
    db.add(audit_log)
    await db.commit()

    # Worker task envelope — matches format expected by scraper worker.py
    worker_task = {
        "task_id": run_id,
        "user_id": "admin",
        "request_id": audit_log.request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_hash": audit_hash,
        "payload": {"type": task_type, **payload},
    }
    await r.rpush("scraper:tasks", json.dumps(worker_task))

    status_key = f"scraper:status:{run_id}"
    await r.set(
        status_key,
        json.dumps({"state": "queued", "companies_found": 0, "jobs_found": 0, "error": None}),
    )

    return run_id


async def get_run_status(run_id: str, r: redis.Redis) -> Optional[dict]:
    """Fetch run status from Redis.

    Args:
        run_id: UUID string of the run.
        r: Redis async client.

    Returns:
        Status dict with run_id included, or None if key not found.
    """
    data = await r.get(f"scraper:status:{run_id}")
    if not data:
        return None
    status = json.loads(data)
    status["run_id"] = run_id
    return status


# ── DB query helpers ──────────────────────────────────────────────────────────

async def get_companies(
    db: AsyncSession,
    crawl_status: Optional[str] = None,
    ats_platform: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """Return paginated company records with optional filters.

    Args:
        db: Async SQLAlchemy session.
        crawl_status: Optional filter by crawl_status.
        ats_platform: Optional filter by ats_platform.
        limit: Page size.
        offset: Pagination offset.

    Returns:
        Tuple of (list of company dicts, total count).
    """
    base_stmt = select(Company)

    if crawl_status:
        base_stmt = base_stmt.where(Company.crawl_status == crawl_status)
    if ats_platform:
        base_stmt = base_stmt.where(Company.ats_platform == ats_platform)

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = base_stmt.order_by(Company.discovery_date.desc()).limit(limit).offset(offset)
    rows = (await db.execute(stmt)).scalars().all()

    return [_company_to_dict(r) for r in rows], total


async def get_company_stats(db: AsyncSession) -> dict:
    """Return aggregated company enrichment statistics.

    Args:
        db: Async SQLAlchemy session.

    Returns:
        Stats dict.
    """
    total = (await db.execute(select(func.count()).select_from(Company))).scalar() or 0

    by_status = {
        r.crawl_status: r.cnt
        for r in (await db.execute(
            select(Company.crawl_status, func.count().label("cnt"))
            .group_by(Company.crawl_status)
        ))
    }

    by_ats = {
        r.ats_platform: r.cnt
        for r in (await db.execute(
            select(Company.ats_platform, func.count().label("cnt"))
            .group_by(Company.ats_platform)
        ))
    }

    with_career_email = (await db.execute(
        select(func.count()).select_from(Company).where(
            func.cardinality(Company.career_emails) > 0
        )
    )).scalar() or 0

    low_trust_count = (await db.execute(
        select(func.count()).select_from(Company).where(
            Company.email_trust == "low_trust"
        )
    )).scalar() or 0

    with_career_page = (await db.execute(
        select(func.count()).select_from(Company).where(
            Company.career_page_url.isnot(None)
        )
    )).scalar() or 0

    return {
        "total_companies": total,
        "by_crawl_status": by_status,
        "by_ats_platform": by_ats,
        "with_career_page_url": with_career_page,
        "with_career_email": with_career_email,
        "low_trust_email_count": low_trust_count,
    }


async def get_latest_jobs(
    db: AsyncSession,
    company_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """Return paginated career job listings.

    Args:
        db: Async SQLAlchemy session.
        company_id: Optional UUID string filter.
        status: Optional status filter.
        limit: Page size.
        offset: Pagination offset.

    Returns:
        Tuple of (list of job dicts, total count).
    """
    base_stmt = select(CareerJob, Company.company_name, Company.apex_domain).join(
        Company, CareerJob.company_id == Company.company_id
    )

    if company_id:
        base_stmt = base_stmt.where(CareerJob.company_id == company_id)
    if status:
        base_stmt = base_stmt.where(CareerJob.status == status)
    else:
        base_stmt = base_stmt.where(CareerJob.status != "closed")

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = base_stmt.order_by(CareerJob.last_seen_at.desc()).limit(limit).offset(offset)
    rows = (await db.execute(stmt)).all()

    jobs = []
    for row in rows:
        job, company_name, apex_domain = row
        jobs.append(_career_job_to_dict(job, company_name, apex_domain))

    return jobs, total


async def get_job_counts(db: AsyncSession) -> dict:
    """Return aggregated career job counts.

    Args:
        db: Async SQLAlchemy session.

    Returns:
        Counts dict.
    """
    total = (await db.execute(select(func.count()).select_from(CareerJob))).scalar() or 0

    by_status = {
        r.status: r.cnt
        for r in (await db.execute(
            select(CareerJob.status, func.count().label("cnt"))
            .group_by(CareerJob.status)
        ))
    }

    by_extraction_method = {
        r.extraction_method: r.cnt
        for r in (await db.execute(
            select(CareerJob.extraction_method, func.count().label("cnt"))
            .group_by(CareerJob.extraction_method)
        ))
    }

    active_company_count = (await db.execute(
        select(func.count(func.distinct(CareerJob.company_id))).where(
            CareerJob.status == "active"
        )
    )).scalar() or 0

    with_apply_contact = (await db.execute(
        select(func.count()).select_from(CareerJob).where(
            (CareerJob.apply_email.isnot(None)) | (CareerJob.apply_url.isnot(None))
        )
    )).scalar() or 0

    return {
        "total_jobs": total,
        "by_status": by_status,
        "by_extraction_method": by_extraction_method,
        "active_companies_count": active_company_count,
        "jobs_with_apply_contact": with_apply_contact,
    }


# ── Private serialisers ───────────────────────────────────────────────────────

def _company_to_dict(row: "Company") -> dict:
    return {
        "company_id": str(row.company_id),
        "company_name": row.company_name,
        "apex_domain": row.apex_domain,
        "career_page_url": row.career_page_url,
        "career_emails": list(row.career_emails or []),
        "email_trust": row.email_trust,
        "ats_platform": row.ats_platform,
        "industry": row.industry,
        "hq_location": row.hq_location,
        "source": row.source,
        "crawl_status": row.crawl_status,
        "discovery_date": row.discovery_date.isoformat() if row.discovery_date else None,
        "last_enriched_at": row.last_enriched_at.isoformat() if row.last_enriched_at else None,
    }


def _career_job_to_dict(
    row: "CareerJob",
    company_name: Optional[str] = None,
    apex_domain: Optional[str] = None,
) -> dict:
    return {
        "career_job_id": str(row.career_job_id),
        "company_id": str(row.company_id),
        "company_name": company_name,
        "apex_domain": apex_domain,
        "job_title": row.job_title,
        "job_url": row.job_url,
        "location": row.location,
        "remote_type": row.remote_type,
        "job_type": row.job_type,
        "salary_min": row.salary_min,
        "salary_max": row.salary_max,
        "experience_min": row.experience_min,
        "experience_max": row.experience_max,
        "skills_required": list(row.skills_required or []),
        "apply_email": row.apply_email,
        "apply_url": row.apply_url,
        "ats_platform": row.ats_platform,
        "extraction_method": row.extraction_method,
        "posted_at": row.posted_at.isoformat() if row.posted_at else None,
        "scraped_at": row.scraped_at.isoformat() if row.scraped_at else None,
        "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
        "status": row.status,
        "source_channel": row.source_channel,
    }
