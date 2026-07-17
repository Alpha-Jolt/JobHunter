"""Auth API routes — /api/auth/*"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from orchestration.api.config import get_settings
from orchestration.auth.dependencies import get_current_user
from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.repository import AuthRepository, UserAlreadyExistsError
from orchestration.auth.service import (
    AuthService,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InactiveUserError,
    WeakPasswordError,
)
from orchestration.db.connection import get_session_factory

router = APIRouter(prefix="/api/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days in seconds


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_db() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _make_service(session: AsyncSession) -> AuthService:
    s = get_settings()
    return AuthService(
        repo=AuthRepository(session),
        jwt_secret=s.auth.jwt_secret,
        jwt_algorithm=s.auth.jwt_algorithm,
        access_expiry_minutes=s.auth.jwt_expiry_minutes,
        refresh_expiry_days=s.auth.refresh_token_expiry_days,
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    s = get_settings()
    kwargs = {
        "key": _REFRESH_COOKIE,
        "value": token,
        "httponly": True,
        "secure": s.auth.cookie_secure,
        "samesite": "lax",
        "max_age": _COOKIE_MAX_AGE,
        "path": "/",
    }
    # Share cookie across app/api subdomains in production
    if s.auth.cookie_domain:
        kwargs["domain"] = s.auth.cookie_domain
    response.set_cookie(**kwargs)


def _clear_refresh_cookie(response: Response) -> None:
    s = get_settings()
    kwargs = {"key": _REFRESH_COOKIE, "path": "/"}
    if s.auth.cookie_domain:
        kwargs["domain"] = s.auth.cookie_domain
    response.delete_cookie(**kwargs)


def _user_to_dict(user: UserRecord) -> dict:
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "role": user.role.value,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def _pw_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _pw_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(_get_db),
):
    """Create a new user account."""
    svc = _make_service(session)
    try:
        access_token, refresh_raw, user = await svc.register(
            email=str(body.email),
            password=body.password,
            role=body.role,
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
        )
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    except WeakPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    _set_refresh_cookie(response, refresh_raw)
    return {"access_token": access_token, "token_type": "bearer", "user": _user_to_dict(user)}


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(_get_db),
):
    """Authenticate and receive JWT + refresh token cookie."""
    svc = _make_service(session)
    from orchestration.core.spans import traced
    try:
        async with traced("Login", user_email=str(body.email)):
            access_token, refresh_raw, user = await svc.login(
                email=str(body.email),
                password=body.password,
            )
    except InactiveUserError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    _set_refresh_cookie(response, refresh_raw)
    return {"access_token": access_token, "token_type": "bearer", "user": _user_to_dict(user)}


@router.get("/me")
async def get_me(
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(_get_db),
):
    """Return current authenticated user profile."""
    from orchestration.db.models import MasterResume
    from sqlalchemy import select
    
    result = await session.execute(select(MasterResume).where(MasterResume.user_id == current_user.user_id))
    resume = result.scalar_one_or_none()
    
    user_dict = _user_to_dict(current_user)
    if resume:
        user_dict["resume"] = {
            "resumeKey": resume.file_path,
            "resumeFileName": resume.file_name
        }
    else:
        user_dict["resume"] = None
        
    return {"user": user_dict}


@router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    body: ChangePasswordRequest,
    current_user: UserRecord = Depends(get_current_user),
    session: AsyncSession = Depends(_get_db),
):
    """Change current user's password. Invalidates all existing sessions."""
    svc = _make_service(session)
    try:
        await svc.change_password(
            user_id_str=str(current_user.user_id),
            current_password=body.current_password,
            new_password=body.new_password,
        )
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    except WeakPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return {"success": True}


@router.post("/refresh")
async def refresh_token(
    response: Response,
    session: AsyncSession = Depends(_get_db),
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias=_REFRESH_COOKIE),
):
    """Rotate refresh token. Requires valid refresh cookie."""
    if not refresh_token_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    svc = _make_service(session)
    try:
        new_access, new_refresh = await svc.refresh(
            refresh_token_raw=refresh_token_cookie,
        )
    except InvalidRefreshTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    _set_refresh_cookie(response, new_refresh)
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    session: AsyncSession = Depends(_get_db),
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias=_REFRESH_COOKIE),
):
    """Revoke refresh token and clear cookie."""
    from orchestration.core.spans import traced
    from orchestration.core.metrics import logout_total
    
    if refresh_token_cookie:
        svc = _make_service(session)
        async with traced("Logout"):
            await svc.logout(
                refresh_token_raw=refresh_token_cookie,
            )
    _clear_refresh_cookie(response)
    logout_total.add(1)
    return {"success": True}
