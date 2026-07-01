"""JWT extraction middleware (informational — auth is done via dependencies)."""

from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class JWTLoggingMiddleware(BaseHTTPMiddleware):
    """Attach parsed JWT subject to request.state for downstream logging.

    Does NOT enforce auth — that is handled by require_role / get_current_user
    FastAPI dependencies. This middleware only enriches request.state.user_id
    for structured logging when a valid Bearer token is present.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            from opentelemetry import trace
            tracer = trace.get_tracer("jobhunter.orchestration")
            with tracer.start_as_current_span("JWT Verification"):
                try:
                    from orchestration.api.config import get_settings
                    from orchestration.auth.tokens import decode_access_token
                    s = get_settings()
                    payload = decode_access_token(token, s.auth.jwt_secret, s.auth.jwt_algorithm)
                    request.state.user_id = payload.sub
                except Exception:
                    pass  # invalid/expired token — let dependency layer handle it
        return await call_next(request)
