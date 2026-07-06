import asyncio
import json
import logging
from scraper.config import config
from dev_mode.dev_runner import DevModeRunner
from scraper.db.connection import init_db, get_session
from scraper.config import config
import redis.asyncio as redis

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)

async def process_task(task_data: dict, r: redis.Redis):
    task_id = task_data.get("task_id")
    payload = task_data.get("payload", {})
    source = payload.get("source", "naukri")
    keywords = payload.get("keywords", [])
    locations = payload.get("locations", [])
    experience = payload.get("experience", "")

    status_key = f"scraper:status:{task_id}"
    await r.set(status_key, json.dumps({"state": "running", "raw": 0, "final": 0, "error": None}))

    logger.info(f"Processing task {task_id} for source {source}")

    task_type = payload.get("type", "scrape")

    if task_type == "company_discovery_bootstrap":
        await _handle_company_discovery_bootstrap(task_id, payload, r, status_key)
    elif task_type == "search_discovery":
        await _handle_search_discovery(task_id, payload, r, status_key)
    elif task_type == "company_email_refresh":
        await _handle_email_refresh(task_id, payload, r, status_key)
    elif task_type == "career_page_scrape":
        await _handle_career_page_scrape(task_id, payload, r, status_key)
    elif task_type == "ats_api_refresh":
        await _handle_ats_api_refresh(task_id, payload, r, status_key)
    else:
        # Legacy scrape task
        runner = DevModeRunner()
        try:
            result = await runner.run_full_pipeline(
                source=source,
                keywords=keywords,
                locations=locations,
                experience=experience
            )
            logger.info(f"Task {task_id} completed successfully")
            await r.set(status_key, json.dumps({
                "state": "completed",
                "raw": result.raw_jobs_count,
                "final": result.final_jobs_count,
                "error": None
            }))
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            await r.set(status_key, json.dumps({
                "state": "failed",
                "raw": 0,
                "final": 0,
                "error": str(e)
            }))

async def main():
    r = redis.from_url(config.redis_url or "redis://redis:6379/0", decode_responses=True)
    init_db(config.database_url)
    logger.info("Scraper worker started, waiting for tasks...")

    # Limit concurrent tasks to prevent Chromium OOM
    sem = asyncio.Semaphore(2)

    async def _sem_task(data):
        async with sem:
            await process_task(data, r)

    while True:
        try:
            # blpop blocks until an item is available
            result = await r.blpop("scraper:tasks", timeout=5)
            if result:
                queue_name, task_json = result
                task_data = json.loads(task_json)
                logger.info(f"Received task: {task_data.get('task_id')}")

                # Bounded concurrent execution
                asyncio.create_task(_sem_task(task_data))
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error pulling from queue: {e}")
            await asyncio.sleep(5)

# --- Company discovery task handlers ----------------------------------------

async def _handle_company_discovery_bootstrap(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Handle bootstrap company discovery run."""
    from scraper.core.rate_limiter import RateLimiter
    from scraper.core.retry_handler import RetryHandler
    from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker
    from scraper.sources.company_discovery.enrichment.enrichment_pipeline import EnrichmentPipeline
    from scraper.sources.company_discovery.bootstrap.dataset_importer import DatasetImporter
    from scraper.sources.company_discovery.bootstrap.vc_portfolio_crawler import VCPortfolioCrawler
    from scraper.sources.company_discovery.bootstrap.github_org_crawler import GitHubOrgCrawler
    from scraper.sources.company_discovery.bootstrap.directory_crawler import DirectoryCrawler

    await r.set(status_key, json.dumps({"state": "running", "companies_found": 0, "error": None}))

    try:
        rate_limiter = RateLimiter()
        retry_handler = RetryHandler()
        robots_checker = RobotsChecker()
        pipeline = EnrichmentPipeline(robots_checker=robots_checker)

        all_domains = []
        sources = payload.get("sources", ["all"])

        if "all" in sources or "datasets" in sources:
            importer = DatasetImporter(rate_limiter=rate_limiter, retry_handler=retry_handler)
            domains = await importer.discover()
            all_domains.extend(domains)

        if "all" in sources or "vc_portfolio" in sources:
            vc = VCPortfolioCrawler(robots_checker=robots_checker, rate_limiter=rate_limiter, retry_handler=retry_handler)
            domains = await vc.discover()
            all_domains.extend(domains)

        if "all" in sources or "github" in sources:
            gh = GitHubOrgCrawler(rate_limiter=rate_limiter, retry_handler=retry_handler)
            domains = await gh.discover()
            all_domains.extend(domains)

        if "all" in sources or "directory" in sources:
            dc = DirectoryCrawler(robots_checker=robots_checker, rate_limiter=rate_limiter, retry_handler=retry_handler)
            domains = await dc.discover()
            all_domains.extend(domains)

        enriched_count = 0
        async with get_session() as session:
            for domain in all_domains:
                record = await pipeline.enrich(
                    raw_domain=domain,
                    source="bootstrap_dataset",
                )
                if record:
                    await _upsert_company(record, session)
                    enriched_count += 1

        logger.info(f"Bootstrap task {task_id} complete: {enriched_count} companies enriched")
        await r.set(status_key, json.dumps({
            "state": "completed",
            "companies_found": enriched_count,
            "error": None,
        }))
    except Exception as e:
        logger.error(f"Bootstrap task {task_id} failed: {e}", exc_info=True)
        await r.set(status_key, json.dumps({
            "state": "failed",
            "companies_found": 0,
            "error": str(e),
        }))


async def _handle_search_discovery(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Handle admin-initiated keyword search discovery run."""
    from scraper.core.rate_limiter import RateLimiter
    from scraper.core.retry_handler import RetryHandler
    from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker
    from scraper.sources.company_discovery.enrichment.enrichment_pipeline import EnrichmentPipeline
    from scraper.sources.company_discovery.discovery.search_discovery import SearchDiscovery

    await r.set(status_key, json.dumps({"state": "running", "companies_found": 0, "error": None}))

    try:
        rate_limiter = RateLimiter()
        retry_handler = RetryHandler()
        robots_checker = RobotsChecker()
        pipeline = EnrichmentPipeline(robots_checker=robots_checker)

        searcher = SearchDiscovery(rate_limiter=rate_limiter, retry_handler=retry_handler)
        domains = await searcher.discover(
            role=payload.get("role", ""),
            location=payload.get("location", ""),
            experience=payload.get("experience", "fresher"),
            salary=payload.get("salary"),
        )

        enriched_count = 0
        async with get_session() as session:
            for domain in domains:
                record = await pipeline.enrich(
                    raw_domain=domain,
                    source="search_discovery",
                    source_detail=f"{payload.get('role')} {payload.get('location')}",
                )
                if record:
                    await _upsert_company(record, session)
                    enriched_count += 1

        logger.info(f"Search discovery task {task_id} complete: {enriched_count} companies")
        await r.set(status_key, json.dumps({
            "state": "completed",
            "companies_found": enriched_count,
            "error": None,
        }))
    except Exception as e:
        logger.error(f"Search discovery task {task_id} failed: {e}", exc_info=True)
        await r.set(status_key, json.dumps({
            "state": "failed",
            "companies_found": 0,
            "error": str(e),
        }))


async def _handle_email_refresh(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Re-crawl email addresses for companies due for monthly refresh."""
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import select, or_
    from scraper.sources.company_discovery.enrichment.email_extractor import EmailExtractor

    await r.set(status_key, json.dumps({"state": "running", "refreshed": 0, "error": None}))

    try:
        # Import ORM models from the scraper's own DB — these share the same
        # physical schema as the orchestration models but are declared separately
        # to keep the scraper decoupled from the orchestration package.
        from scraper.db.models import Base as _ScraperBase
        # Company model lives in the shared schema; use raw SQL via text() to
        # avoid a hard import of the orchestration ORM into the scraper.
        from sqlalchemy import text

        company_ids = payload.get("company_ids")
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        extractor = EmailExtractor()
        refreshed = 0

        async with get_session() as session:
            if company_ids:
                result = await session.execute(
                    text(
                        "SELECT company_id, apex_domain, career_emails, contact_emails "
                        "FROM companies WHERE company_id = ANY(:ids) "
                        "AND crawl_status = 'enriched' AND robots_txt_allowed = true"
                    ),
                    {"ids": company_ids},
                )
            else:
                result = await session.execute(
                    text(
                        "SELECT company_id, apex_domain, career_emails, contact_emails "
                        "FROM companies WHERE (email_last_crawled_at IS NULL "
                        "OR email_last_crawled_at < :cutoff) "
                        "AND crawl_status = 'enriched' AND robots_txt_allowed = true"
                    ),
                    {"cutoff": thirty_days_ago},
                )

            rows = result.fetchall()
            now = datetime.now(timezone.utc)

            for row in rows:
                company_id, apex_domain, _career, _contact = row
                try:
                    emails = await extractor.extract(apex_domain)
                    await session.execute(
                        text(
                            "UPDATE companies SET "
                            "career_emails = :career_emails, "
                            "contact_emails = :contact_emails, "
                            "email_last_crawled_at = :now "
                            "WHERE company_id = :cid"
                        ),
                        {
                            "career_emails": emails.get("career_emails", []),
                            "contact_emails": emails.get("contact_emails", []),
                            "now": now,
                            "cid": str(company_id),
                        },
                    )
                    refreshed += 1
                except Exception as exc:
                    logger.warning(
                        f"Email refresh failed for {apex_domain}: {exc}"
                    )

        logger.info(f"Email refresh task {task_id} complete: {refreshed} companies refreshed")
        await r.set(status_key, json.dumps({
            "state": "completed",
            "refreshed": refreshed,
            "error": None,
        }))
    except Exception as e:
        logger.error(f"Email refresh task {task_id} failed: {e}", exc_info=True)
        await r.set(status_key, json.dumps({
            "state": "failed",
            "refreshed": 0,
            "error": str(e),
        }))


async def _handle_career_page_scrape(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Scrape career page jobs for all enriched companies (or one company)."""
    from sqlalchemy import text
    from scraper.sources.career_page.router import CareerPageRouter
    from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker

    await r.set(status_key, json.dumps({"state": "running", "jobs_found": 0, "error": None}))

    try:
        router = CareerPageRouter(robots_checker=RobotsChecker())
        company_id_filter = payload.get("company_id")
        jobs_found = 0

        async with get_session() as session:
            if company_id_filter:
                result = await session.execute(
                    text(
                        "SELECT company_id, apex_domain, career_page_url, ats_platform, "
                        "career_emails FROM companies "
                        "WHERE company_id = :cid AND crawl_status = 'enriched' "
                        "AND career_page_url IS NOT NULL"
                    ),
                    {"cid": str(company_id_filter)},
                )
            else:
                result = await session.execute(
                    text(
                        "SELECT company_id, apex_domain, career_page_url, ats_platform, "
                        "career_emails FROM companies "
                        "WHERE crawl_status = 'enriched' AND career_page_url IS NOT NULL"
                    )
                )

            companies = result.fetchall()

        for company_row in companies:
            company_id, apex_domain, career_page_url, ats_platform, career_emails = company_row
            company_dict = {
                "company_id": str(company_id),
                "apex_domain": apex_domain,
                "career_page_url": career_page_url,
                "ats_platform": ats_platform or "none",
                "career_emails": list(career_emails or []),
            }

            try:
                extracted_jobs = await router.extract_jobs(company_dict)
                if not extracted_jobs:
                    continue

                seen_url_hashes = {j["url_hash"] for j in extracted_jobs}

                async with get_session() as session:
                    # Fetch existing url_hashes for this company
                    existing_result = await session.execute(
                        text(
                            "SELECT url_hash FROM career_jobs WHERE company_id = :cid"
                        ),
                        {"cid": str(company_id)},
                    )
                    existing_url_hashes = {row[0] for row in existing_result.fetchall()}

                    # Upsert extracted jobs
                    upserted = await _upsert_career_jobs(extracted_jobs, session)
                    jobs_found += upserted

                    # Mark jobs not seen this crawl as closed
                    closed_hashes = router.mark_closed_jobs(existing_url_hashes, seen_url_hashes)
                    if closed_hashes:
                        await session.execute(
                            text(
                                "UPDATE career_jobs SET status = 'closed' "
                                "WHERE company_id = :cid AND url_hash = ANY(:hashes)"
                            ),
                            {"cid": str(company_id), "hashes": list(closed_hashes)},
                        )

                await r.set(status_key, json.dumps({
                    "state": "running",
                    "jobs_found": jobs_found,
                    "error": None,
                }))
            except Exception as exc:
                logger.warning(
                    f"Career page scrape failed for {apex_domain}: {exc}"
                )

        logger.info(f"Career page scrape task {task_id} complete: {jobs_found} jobs found")
        await r.set(status_key, json.dumps({
            "state": "completed",
            "jobs_found": jobs_found,
            "error": None,
        }))
    except Exception as e:
        logger.error(f"Career page scrape task {task_id} failed: {e}", exc_info=True)
        await r.set(status_key, json.dumps({
            "state": "failed",
            "jobs_found": 0,
            "error": str(e),
        }))


async def _handle_ats_api_refresh(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Re-pull jobs from Greenhouse/Lever/Ashby ATS APIs."""
    from sqlalchemy import text
    from scraper.sources.career_page.router import CareerPageRouter
    from scraper.sources.company_discovery.enrichment.robots_checker import RobotsChecker

    await r.set(status_key, json.dumps({"state": "running", "jobs_found": 0, "error": None}))

    try:
        router = CareerPageRouter(robots_checker=RobotsChecker())
        jobs_found = 0

        async with get_session() as session:
            result = await session.execute(
                text(
                    "SELECT company_id, apex_domain, career_page_url, ats_platform, "
                    "career_emails FROM companies "
                    "WHERE ats_platform IN ('greenhouse', 'lever', 'ashby') "
                    "AND crawl_status = 'enriched'"
                )
            )
            companies = result.fetchall()

        for company_row in companies:
            company_id, apex_domain, career_page_url, ats_platform, career_emails = company_row
            company_dict = {
                "company_id": str(company_id),
                "apex_domain": apex_domain,
                "career_page_url": career_page_url or f"https://{apex_domain}/jobs",
                "ats_platform": ats_platform,
                "career_emails": list(career_emails or []),
            }

            try:
                extracted_jobs = await router.extract_jobs(company_dict)
                if not extracted_jobs:
                    continue

                seen_url_hashes = {j["url_hash"] for j in extracted_jobs}

                async with get_session() as session:
                    existing_result = await session.execute(
                        text(
                            "SELECT url_hash FROM career_jobs WHERE company_id = :cid"
                        ),
                        {"cid": str(company_id)},
                    )
                    existing_url_hashes = {row[0] for row in existing_result.fetchall()}

                    upserted = await _upsert_career_jobs(extracted_jobs, session)
                    jobs_found += upserted

                    closed_hashes = router.mark_closed_jobs(existing_url_hashes, seen_url_hashes)
                    if closed_hashes:
                        await session.execute(
                            text(
                                "UPDATE career_jobs SET status = 'closed' "
                                "WHERE company_id = :cid AND url_hash = ANY(:hashes)"
                            ),
                            {"cid": str(company_id), "hashes": list(closed_hashes)},
                        )

                await r.set(status_key, json.dumps({
                    "state": "running",
                    "jobs_found": jobs_found,
                    "error": None,
                }))
            except Exception as exc:
                logger.warning(
                    f"ATS API refresh failed for {apex_domain}: {exc}"
                )

        logger.info(f"ATS API refresh task {task_id} complete: {jobs_found} jobs found")
        await r.set(status_key, json.dumps({
            "state": "completed",
            "jobs_found": jobs_found,
            "error": None,
        }))
    except Exception as e:
        logger.error(f"ATS API refresh task {task_id} failed: {e}", exc_info=True)
        await r.set(status_key, json.dumps({
            "state": "failed",
            "jobs_found": 0,
            "error": str(e),
        }))


# --- Shared helpers ---------------------------------------------------------

async def _upsert_company(record: dict, session) -> None:
    """Upsert a single enriched company dict into the companies table.

    On conflict (apex_domain): updates enrichment fields and merges email arrays.
    On new: inserts full record.

    Args:
        record: Dict returned by EnrichmentPipeline.enrich().
        session: Active SQLAlchemy async session.
    """
    import uuid as _uuid
    from sqlalchemy import text

    if not record or not record.get("apex_domain"):
        return

    try:
        await session.execute(
            text("""
                INSERT INTO companies (
                    company_id, company_name, normalized_name, apex_domain,
                    subdomains, career_page_url, career_emails, contact_emails,
                    email_trust, ats_platform, industry, hq_location,
                    source, source_detail, robots_txt_allowed,
                    discovery_date, last_enriched_at, email_last_crawled_at,
                    crawl_status, dedup_fingerprint
                ) VALUES (
                    :company_id, :company_name, :normalized_name, :apex_domain,
                    :subdomains, :career_page_url, :career_emails, :contact_emails,
                    :email_trust, :ats_platform, :industry, :hq_location,
                    :source, :source_detail, :robots_txt_allowed,
                    :discovery_date, :last_enriched_at, :email_last_crawled_at,
                    :crawl_status, :dedup_fingerprint
                )
                ON CONFLICT (apex_domain) DO UPDATE SET
                    career_page_url = COALESCE(EXCLUDED.career_page_url, companies.career_page_url),
                    career_emails = (
                        SELECT ARRAY(SELECT DISTINCT UNNEST(companies.career_emails || EXCLUDED.career_emails))
                    ),
                    contact_emails = (
                        SELECT ARRAY(SELECT DISTINCT UNNEST(companies.contact_emails || EXCLUDED.contact_emails))
                    ),
                    ats_platform = CASE
                        WHEN companies.ats_platform = 'none' THEN EXCLUDED.ats_platform
                        ELSE companies.ats_platform
                    END,
                    last_enriched_at = EXCLUDED.last_enriched_at,
                    email_last_crawled_at = EXCLUDED.email_last_crawled_at,
                    crawl_status = EXCLUDED.crawl_status
            """),
            {
                "company_id": str(record.get("company_id") or _uuid.uuid4()),
                "company_name": record.get("company_name"),
                "normalized_name": record.get("normalized_name"),
                "apex_domain": record["apex_domain"],
                "subdomains": record.get("subdomains", []),
                "career_page_url": record.get("career_page_url"),
                "career_emails": record.get("career_emails", []),
                "contact_emails": record.get("contact_emails", []),
                "email_trust": record.get("email_trust", "unverified"),
                "ats_platform": record.get("ats_platform", "none"),
                "industry": record.get("industry"),
                "hq_location": record.get("hq_location"),
                "source": record.get("source", "bootstrap_dataset"),
                "source_detail": record.get("source_detail"),
                "robots_txt_allowed": record.get("robots_txt_allowed"),
                "discovery_date": record.get("discovery_date"),
                "last_enriched_at": record.get("last_enriched_at"),
                "email_last_crawled_at": record.get("email_last_crawled_at"),
                "crawl_status": record.get("crawl_status", "enriched"),
                "dedup_fingerprint": record.get("dedup_fingerprint", ""),
            },
        )
        await session.commit()
    except Exception as exc:
        logger.warning(f"Upsert failed for company {record.get('apex_domain')}: {exc}")
        await session.rollback()


async def _upsert_career_jobs(jobs: list[dict], session) -> int:
    """Upsert a list of extracted job dicts into the career_jobs table.

    On conflict (company_id, url_hash): updates content_hash, last_seen_at,
    and any changed fields. On new: inserts with status 'raw'.

    Args:
        jobs: List of enriched job dicts from CareerPageRouter.extract_jobs().
        session: Active SQLAlchemy async session.

    Returns:
        Number of rows upserted.
    """
    from datetime import datetime, timezone
    from sqlalchemy import text

    if not jobs:
        return 0

    now = datetime.now(timezone.utc)
    upserted = 0

    def _to_dt(val):
        """Convert ISO string to datetime if needed; return datetime or None."""
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        try:
            return datetime.fromisoformat(str(val))
        except (ValueError, TypeError):
            return None

    for job in jobs:
        try:
            await session.execute(
                text("""
                    INSERT INTO career_jobs (
                        career_job_id, company_id, job_title, job_url, url_hash,
                        content_hash, description, skills_required, location,
                        remote_type, salary_min, salary_max, experience_min,
                        experience_max, job_type, apply_email, apply_url,
                        ats_platform, extraction_method, posted_at,
                        scraped_at, last_seen_at, status, source_channel
                    ) VALUES (
                        :career_job_id, :company_id, :job_title, :job_url, :url_hash,
                        :content_hash, :description, :skills_required, :location,
                        :remote_type, :salary_min, :salary_max, :experience_min,
                        :experience_max, :job_type, :apply_email, :apply_url,
                        :ats_platform, :extraction_method, :posted_at,
                        :scraped_at, :last_seen_at, :status, :source_channel
                    )
                    ON CONFLICT (company_id, url_hash) DO UPDATE SET
                        content_hash = EXCLUDED.content_hash,
                        last_seen_at = EXCLUDED.last_seen_at,
                        job_title = EXCLUDED.job_title,
                        description = EXCLUDED.description,
                        skills_required = EXCLUDED.skills_required,
                        location = EXCLUDED.location,
                        remote_type = EXCLUDED.remote_type,
                        salary_min = EXCLUDED.salary_min,
                        salary_max = EXCLUDED.salary_max,
                        experience_min = EXCLUDED.experience_min,
                        experience_max = EXCLUDED.experience_max,
                        apply_email = EXCLUDED.apply_email,
                        apply_url = EXCLUDED.apply_url,
                        status = CASE
                            WHEN career_jobs.status = 'closed' THEN 'active'
                            ELSE career_jobs.status
                        END
                """),
                {
                    "career_job_id": job.get("career_job_id"),
                    "company_id": job.get("company_id"),
                    "job_title": job.get("job_title", ""),
                    "job_url": job.get("job_url", ""),
                    "url_hash": job.get("url_hash", ""),
                    "content_hash": job.get("content_hash", ""),
                    "description": job.get("description"),
                    "skills_required": job.get("skills_required", []),
                    "location": job.get("location"),
                    "remote_type": job.get("remote_type"),
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "experience_min": job.get("experience_min"),
                    "experience_max": job.get("experience_max"),
                    "job_type": job.get("job_type"),
                    "apply_email": job.get("apply_email"),
                    "apply_url": job.get("apply_url"),
                    "ats_platform": job.get("ats_platform"),
                    "extraction_method": job.get("extraction_method", "html_parse"),
                    "posted_at": _to_dt(job.get("posted_at")),
                    "scraped_at": _to_dt(job.get("scraped_at")) or now,
                    "last_seen_at": _to_dt(job.get("last_seen_at")) or now,
                    "status": job.get("status", "raw"),
                    "source_channel": job.get("source_channel", "career_page"),
                },
            )
            upserted += 1
        except Exception as exc:
            logger.warning(
                f"Upsert failed for job {job.get('url_hash')}: {exc}"
            )

    return upserted


if __name__ == "__main__":
    asyncio.run(main())
