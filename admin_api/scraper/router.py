import uuid
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from auth.dependencies import require_admin_session
from core.db import get_db
from core.redis import get_redis
from scraper.service import save_preferences_and_audit, enqueue_scrape_task, get_scraper_status
from core.config import settings

router = APIRouter(dependencies=[Depends(require_admin_session)])

class ScraperTriggerRequest(BaseModel):
    source: str
    keywords: list[str]
    locations: list[str]
    experience: str = ""
    custom_fields: dict = {}

@router.post("/trigger")
async def trigger_scraper(
    req: Request,
    payload: ScraperTriggerRequest,
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis)
):
    # Retrieve user_id from request state (set by require_admin_session dependency at router level)
    # Alternatively, use settings.ADMIN_EMAIL since it's a single admin system
    user_id = settings.ADMIN_EMAIL
    
    # Unique Request ID
    request_id = str(uuid.uuid4())
    
    # Save preferences and audit log
    task_id, audit_hash = await save_preferences_and_audit(
        db=db,
        user_id=user_id,
        request_id=request_id,
        payload=payload.model_dump()
    )

    # Push to redis task queue
    await enqueue_scrape_task(
        task_id=task_id,
        user_id=user_id,
        request_id=request_id,
        audit_hash=audit_hash,
        payload=payload.model_dump(),
        r=r
    )

    return {"task_id": task_id, "status": "queued"}

@router.get("/status/{task_id}")
async def fetch_status(task_id: str, r: redis.Redis = Depends(get_redis)):
    status = await get_scraper_status(task_id, r)
    return status

@router.get("/logs")
async def fetch_logs(limit: int = 100):
    try:
        with open(settings.SCRAPER_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return {"logs": lines[-limit:]}
    except Exception as e:
        return {"logs": [f"Could not read logs: {str(e)}"]}
