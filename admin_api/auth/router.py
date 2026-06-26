import logging
import secrets
from datetime import timedelta

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from auth.models import LoginRequest, TokenResponse
from auth.service import verify_password, create_access_token
from core.config import settings
from core.rate_limit import limiter
from core.redis import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    redis_client: redis.Redis = Depends(get_redis),
):
    failures_key = f"auth_failures:{login_data.email}"
    failures = await redis_client.get(failures_key)
    if failures and int(failures) >= 10:
        logger.warning(f"Account lockout triggered for {login_data.email}")
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")

    if login_data.email != settings.ADMIN_EMAIL or not verify_password(login_data.password, settings.ADMIN_PASSWORD_HASH):
        await redis_client.incr(failures_key)
        await redis_client.expire(failures_key, 300)
        logger.warning(f"Failed login attempt for {login_data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    await redis_client.delete(failures_key)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": settings.ADMIN_EMAIL}, expires_delta=access_token_expires)

    refresh_token = secrets.token_hex(32)
    refresh_key = f"refresh_token:{refresh_token}"
    await redis_client.setex(refresh_key, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), settings.ADMIN_EMAIL)

    response.set_cookie(
        key="admin_refresh",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    logger.info(f"Successful login for {login_data.email}")
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    redis_client: redis.Redis = Depends(get_redis),
):
    old_refresh_token = request.cookies.get("admin_refresh")
    if not old_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    refresh_key = f"refresh_token:{old_refresh_token}"
    email = await redis_client.get(refresh_key)

    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    await redis_client.delete(refresh_key)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)

    new_refresh_token = secrets.token_hex(32)
    new_refresh_key = f"refresh_token:{new_refresh_token}"
    await redis_client.setex(new_refresh_key, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), email)

    response.set_cookie(
        key="admin_refresh",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    redis_client: redis.Redis = Depends(get_redis),
):
    refresh_token = request.cookies.get("admin_refresh")
    if refresh_token:
        await redis_client.delete(f"refresh_token:{refresh_token}")

    response.delete_cookie(
        "admin_refresh",
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
    )
    return {"status": "logged_out"}
