"""Custom middleware for JobHunter orchestration API."""

import logging
import time
import uuid

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique X-Request-ID header to every request and response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status code, and duration for every request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(request.state, "request_id", "-")
        logger.info(
            "%s %s %d %.1fms req_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return a structured JSON error response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "-")
            logger.exception("Unhandled error req_id=%s: %s", request_id, exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred.",
                    "request_id": request_id,
                },
            )


CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://jobhunter.app",
]


def add_cors(app) -> None:
    """Register CORSMiddleware on the FastAPI app.

    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

import hashlib
from opentelemetry import trace

class OTelContextMiddleware(BaseHTTPMiddleware):
    """Enrich the active OTEL span with request context fields."""

    async def dispatch(self, request: Request, call_next) -> Response:
        span = trace.get_current_span()
        if span.is_recording():
            request_id = getattr(request.state, "request_id", "")
            user_id = getattr(request.state, "user_id", "")
            
            # Secure session ID hash
            refresh_token = request.cookies.get("refresh_token")
            session_id = hashlib.sha256(refresh_token.encode()).hexdigest() if refresh_token else ""

            span.set_attribute("request.id", request_id)
            span.set_attribute("user.id", str(user_id) if user_id else "")
            span.set_attribute("session.id", session_id)

        response = await call_next(request)

        ctx = span.get_span_context()
        if ctx and ctx.is_valid:
            response.headers["X-Trace-ID"] = format(ctx.trace_id, "032x")
        return response
