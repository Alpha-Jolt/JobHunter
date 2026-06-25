import pytest
from httpx import AsyncClient, ASGITransport
from app import app
from core.config import settings

@pytest.mark.asyncio
async def test_unauthorized_scraper_trigger():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/scraper/trigger", 
            json={"source": "naukri", "keywords": [], "locations": []}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
