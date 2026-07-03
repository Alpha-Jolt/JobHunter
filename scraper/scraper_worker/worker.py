import asyncio
import json
import logging
from uuid import uuid4
from scraper.config import config
from dev_mode.dev_runner import DevModeRunner
from scraper.db.connection import init_db
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

if __name__ == "__main__":
    asyncio.run(main())


# --- Company discovery task handlers ----------------------------------------

async def _handle_company_discovery_bootstrap(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Handle bootstrap company discovery run."""
    import uuid
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
        for domain in all_domains:
            record = await pipeline.enrich(
                raw_domain=domain,
                source="bootstrap_dataset",
            )
            if record:
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
        for domain in domains:
            record = await pipeline.enrich(
                raw_domain=domain,
                source="search_discovery",
                source_detail=f"{payload.get('role')} {payload.get('location')}",
            )
            if record:
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
    from scraper.sources.company_discovery.enrichment.email_extractor import EmailExtractor

    await r.set(status_key, json.dumps({"state": "running", "refreshed": 0, "error": None}))

    try:
        extractor = EmailExtractor()
        # Placeholder — full registry integration happens when DPL is wired to the worker
        logger.info(f"Email refresh task {task_id} triggered (registry integration pending)")
        await r.set(status_key, json.dumps({
            "state": "completed",
            "refreshed": 0,
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
    """Trigger career page job scrape for all enriched companies (or one specific company)."""
    await r.set(status_key, json.dumps({"state": "running", "jobs_found": 0, "error": None}))
    # Career page scrape (Module 2) — implemented in Phase 3
    logger.info(f"Career page scrape task {task_id} queued (Module 2 pending)")
    await r.set(status_key, json.dumps({
        "state": "completed",
        "jobs_found": 0,
        "error": None,
    }))


async def _handle_ats_api_refresh(
    task_id: str, payload: dict, r, status_key: str
) -> None:
    """Trigger ATS API re-pull for Greenhouse/Lever/Ashby companies."""
    await r.set(status_key, json.dumps({"state": "running", "jobs_found": 0, "error": None}))
    # ATS API refresh (Module 2) — implemented in Phase 3
    logger.info(f"ATS API refresh task {task_id} queued (Module 2 pending)")
    await r.set(status_key, json.dumps({
        "state": "completed",
        "jobs_found": 0,
        "error": None,
    }))
