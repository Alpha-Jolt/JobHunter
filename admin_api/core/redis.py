import redis.asyncio as redis
from core.config import settings

async def get_redis() -> redis.Redis:
    return redis.from_url(settings.REDIS_URL, decode_responses=True)
