"""Unit tests for auth/dependencies.py — get_current_user, require_role."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from orchestration.auth.dependencies import get_current_user, require_role
from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.tokens import encode_access_token

_SECRET = "test-secret-key-that-is-32-chars!!"
_ALG = "HS256"


def _make_user(role=RoleEnum.HUNTER, is_active=True, user_id=None):
    return UserRecord(
        user_id=user_id or uuid.uuid4(),
        email="user@example.com",
        password_hash="hash",
        role=role,
        is_active=is_active,
    )


def _valid_token(user_id: str, role: RoleEnum) -> str:
    return encode_access_token(
        user_id, role, _SECRET, _ALG,
        datetime.now(timezone.utc) + timedelta(minutes=15),
    )


def _expired_token(user_id: str) -> str:
    return encode_access_token(
        user_id, RoleEnum.HUNTER, _SECRET, _ALG,
        datetime.now(timezone.utc) - timedelta(minutes=1),
    )


def _mock_settings():
    s = MagicMock()
    s.auth.jwt_secret = _SECRET
    s.auth.jwt_algorithm = _ALG
    return s


def _mock_session():
    return AsyncMock()


# ── get_current_user ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    user = _make_user()
    token = _valid_token(str(user.user_id), user.role)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("orchestration.auth.dependencies._get_jwt_config", return_value=(_SECRET, _ALG)), \
         patch("orchestration.auth.dependencies.AuthRepository") as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_user_by_id = AsyncMock(return_value=user)
        MockRepo.return_value = repo_instance

        result = await get_current_user(credentials=creds, session=_mock_session())

    assert result == user


@pytest.mark.asyncio
async def test_get_current_user_no_credentials_raises_401():
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=None, session=_mock_session())
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token_raises_401():
    uid = str(uuid.uuid4())
    token = _expired_token(uid)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("orchestration.auth.dependencies._get_jwt_config", return_value=(_SECRET, _ALG)):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=creds, session=_mock_session())
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_malformed_token_raises_401():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not.a.jwt")
    with patch("orchestration.auth.dependencies._get_jwt_config", return_value=(_SECRET, _ALG)):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=creds, session=_mock_session())
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_user_not_found_raises_401():
    uid = str(uuid.uuid4())
    token = _valid_token(uid, RoleEnum.HUNTER)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("orchestration.auth.dependencies._get_jwt_config", return_value=(_SECRET, _ALG)), \
         patch("orchestration.auth.dependencies.AuthRepository") as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_user_by_id = AsyncMock(return_value=None)
        MockRepo.return_value = repo_instance

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=creds, session=_mock_session())
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_inactive_user_raises_401():
    user = _make_user(is_active=False)
    token = _valid_token(str(user.user_id), user.role)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("orchestration.auth.dependencies._get_jwt_config", return_value=(_SECRET, _ALG)), \
         patch("orchestration.auth.dependencies.AuthRepository") as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_user_by_id = AsyncMock(return_value=user)
        MockRepo.return_value = repo_instance

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=creds, session=_mock_session())
    assert exc.value.status_code == 401


# ── require_role ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_require_role_matching_role_passes():
    user = _make_user(role=RoleEnum.ADMIN)
    dep = require_role(RoleEnum.ADMIN)
    result = await dep(user=user)
    assert result == user


@pytest.mark.asyncio
async def test_require_role_wrong_role_raises_403():
    user = _make_user(role=RoleEnum.HUNTER)
    dep = require_role(RoleEnum.ADMIN)
    with pytest.raises(HTTPException) as exc:
        await dep(user=user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_multiple_allowed_roles():
    user = _make_user(role=RoleEnum.MENTOR)
    dep = require_role(RoleEnum.HUNTER, RoleEnum.MENTOR, RoleEnum.ADMIN)
    result = await dep(user=user)
    assert result == user


@pytest.mark.asyncio
async def test_require_role_hunter_cannot_access_admin():
    user = _make_user(role=RoleEnum.HUNTER)
    dep = require_role(RoleEnum.ADMIN)
    with pytest.raises(HTTPException) as exc:
        await dep(user=user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_recruiter_cannot_access_hunter_endpoint():
    user = _make_user(role=RoleEnum.RECRUITER)
    dep = require_role(RoleEnum.HUNTER)
    with pytest.raises(HTTPException) as exc:
        await dep(user=user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_error_message_contains_role():
    user = _make_user(role=RoleEnum.HUNTER)
    dep = require_role(RoleEnum.ADMIN)
    with pytest.raises(HTTPException) as exc:
        await dep(user=user)
    assert "hunter" in exc.value.detail.lower()
