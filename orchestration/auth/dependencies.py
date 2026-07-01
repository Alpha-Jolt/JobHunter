"""FastAPI auth dependencies — get_current_user, require_role."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.repository import AuthRepository
from orchestration.auth.tokens import TokenError, TokenExpiredError, decode_access_token
from orchestration.db.connection import get_session_factory

_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

_INACTIVE_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Account is inactive",
    headers={"WWW-Authenticate": "Bearer"},
)


async def _get_db_session() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _get_jwt_config() -> tuple[str, str]:
    """Return (jwt_secret, jwt_algorithm) from settings."""
    from orchestration.api.config import get_settings
    s = get_settings()
    return s.auth.jwt_secret, s.auth.jwt_algorithm


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    session: AsyncSession = Depends(_get_db_session),
) -> UserRecord:
    """Extract and validate Bearer JWT; return the authenticated user.

    Raises:
        HTTPException 401: Missing, malformed, expired, or invalid token.
        HTTPException 401: User not found or inactive.
    """
    if not credentials:
        raise _CREDENTIALS_EXCEPTION

    jwt_secret, jwt_algorithm = _get_jwt_config()

    from orchestration.core.metrics import jwt_validation_duration
    from orchestration.core.spans import traced
    import time
    
    start_time = time.perf_counter()
    try:
        payload = decode_access_token(credentials.credentials, jwt_secret, jwt_algorithm)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenError:
        raise _CREDENTIALS_EXCEPTION
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        jwt_validation_duration.record(duration_ms)

    import uuid
    try:
        user_id = uuid.UUID(payload.sub)
    except ValueError:
        raise _CREDENTIALS_EXCEPTION

    repo = AuthRepository(session)
    async with traced("Session Validation"):
        user = await repo.get_user_by_id(user_id)

    if not user:
        raise _CREDENTIALS_EXCEPTION
    if not user.is_active:
        raise _INACTIVE_EXCEPTION

    return user


def require_role(*roles: RoleEnum):
    """Dependency factory: enforce that the current user has one of the given roles.

    Usage::

        @router.get("/admin/users", dependencies=[Depends(require_role(RoleEnum.ADMIN))])

    Raises:
        HTTPException 403: User role not in allowed roles.
    """
    async def _check(user: UserRecord = Depends(get_current_user)) -> UserRecord:
        from orchestration.core.spans import traced
        async with traced("RBAC", required_roles=[r.value for r in roles], user_role=user.role.value):
            if user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{user.role.value}' is not authorized for this action",
                )
            return user

    return _check
