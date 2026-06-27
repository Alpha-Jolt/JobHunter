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
