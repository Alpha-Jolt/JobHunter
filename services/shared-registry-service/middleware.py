"""Auth, logging middleware and unhandled exception handler."""

import uuid
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import get_settings

logger = structlog.get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/health/ready"):
            return await call_next(request)

        settings = get_settings()
        if not settings.auth_enabled:
            return await call_next(request)

        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token or token != settings.api_key_token:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTH_FAILED",
                        "message": "Invalid or missing API key",
                        "status": 401,
                    }
                },
            )

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = datetime.now(timezone.utc)
        response = await call_next(request)
        duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        logger.info(
            "api_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response


def add_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = str(uuid.uuid4())
        logger.error(
            "unhandled_exception",
            request_id=request_id,
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "status": 500,
                    "request_id": request_id,
                }
            },
        )
