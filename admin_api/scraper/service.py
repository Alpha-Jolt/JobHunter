import json
import hashlib
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scraper.models import ScraperPreferences, ScraperAuditLog


def generate_audit_hash(prev_hash: str, payload_str: str) -> str:
    combined = f"{prev_hash}|{payload_str}"
    return hashlib.sha256(combined.encode()).hexdigest()


async def save_preferences_and_audit(
    db: AsyncSession,
    user_id: str,
    request_id: str,
    payload: dict,
) -> tuple[str, str]:
    prefs = ScraperPreferences(user_id=user_id, preferences=payload)
    db.add(prefs)

    result = await db.execute(select(ScraperAuditLog).order_by(ScraperAuditLog.id.desc()).limit(1))
    last_log = result.scalars().first()
    prev_hash = last_log.audit_hash if last_log else "genesis"

    task_id = str(uuid.uuid4())
    payload_str = json.dumps(payload, sort_keys=True)
    audit_hash = generate_audit_hash(prev_hash, payload_str)

    audit_log = ScraperAuditLog(
        task_id=task_id,
        user_id=user_id,
        request_id=request_id,
        audit_hash=audit_hash,
        payload=payload,
    )
    db.add(audit_log)
    await db.commit()

    return task_id, audit_hash


async def enqueue_scrape_task(
    task_id: str,
    user_id: str,
    request_id: str,
    audit_hash: str,
    payload: dict,
    r: redis.Redis,
):
    task_data = {
        "task_id": task_id,
        "user_id": user_id,
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_hash": audit_hash,
        "payload": payload,
    }
    await r.rpush("scraper:tasks", json.dumps(task_data))

    status_key = f"scraper:status:{task_id}"
    await r.set(status_key, json.dumps({"state": "queued", "raw": 0, "final": 0, "error": None}))


async def get_scraper_status(task_id: str, r: redis.Redis) -> dict:
    status_key = f"scraper:status:{task_id}"
    data = await r.get(status_key)
    if data:
        return json.loads(data)
    return {"state": "unknown", "raw": 0, "final": 0, "error": None}
