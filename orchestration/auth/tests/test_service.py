"""Unit tests for auth/service.py."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from orchestration.auth.hashing import hash_password
from orchestration.auth.models.tokens import RefreshTokenRecord
from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.repository import UserAlreadyExistsError
from orchestration.auth.service import (
    AuthService,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InactiveUserError,
    WeakPasswordError,
)
from orchestration.auth.tokens import generate_refresh_token, hash_token

_SECRET = "test-secret-key-that-is-32-chars!!"
_ALG = "HS256"


def _make_service(repo: AsyncMock) -> AuthService:
    return AuthService(
        repo=repo,
        jwt_secret=_SECRET,
        jwt_algorithm=_ALG,
        access_expiry_minutes=15,
        refresh_expiry_days=30,
    )


def _make_user(role=RoleEnum.HUNTER, is_active=True) -> UserRecord:
    return UserRecord(
        user_id=uuid.uuid4(),
        email="user@example.com",
        password_hash=hash_password("password123"),
        role=role,
        is_active=is_active,
    )


def _make_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.create_user = AsyncMock()
    repo.get_user_by_email = AsyncMock()
    repo.get_user_by_id = AsyncMock()
    repo.save_refresh_token = AsyncMock()
    repo.get_active_refresh_token = AsyncMock()
    repo.revoke_refresh_token = AsyncMock()
    repo.revoke_all_user_tokens = AsyncMock()
    repo.update_last_login = AsyncMock()
    repo.update_password = AsyncMock()
    return repo


def _make_token_record(user_id, token_hash):
    return RefreshTokenRecord(
        token_id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        issued_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )


# ── register ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_returns_tokens_and_user():
    repo = _make_repo()
    user = _make_user()
    repo.create_user.return_value = user
    repo.save_refresh_token.return_value = MagicMock()
    svc = _make_service(repo)

    access, refresh, returned_user = await svc.register("user@example.com", "password123", RoleEnum.HUNTER)

    assert isinstance(access, str) and len(access) > 0
    assert isinstance(refresh, str) and len(refresh) > 0
    assert returned_user == user
    repo.create_user.assert_called_once()
    repo.save_refresh_token.assert_called_once()


@pytest.mark.asyncio
async def test_register_weak_password_raises():
    repo = _make_repo()
    svc = _make_service(repo)
    with pytest.raises(WeakPasswordError):
        await svc.register("user@example.com", "short", RoleEnum.HUNTER)


@pytest.mark.asyncio
async def test_register_invalid_email_raises():
    repo = _make_repo()
    svc = _make_service(repo)
    with pytest.raises(ValueError):
        await svc.register("not-an-email", "password123", RoleEnum.HUNTER)


@pytest.mark.asyncio
async def test_register_duplicate_email_propagates():
    repo = _make_repo()
    repo.create_user.side_effect = UserAlreadyExistsError("dup")
    svc = _make_service(repo)
    with pytest.raises(UserAlreadyExistsError):
        await svc.register("dup@example.com", "password123", RoleEnum.HUNTER)


@pytest.mark.asyncio
async def test_register_all_roles():
    for role in RoleEnum:
        repo = _make_repo()
        user = _make_user(role=role)
        repo.create_user.return_value = user
        repo.save_refresh_token.return_value = MagicMock()
        svc = _make_service(repo)
        _, _, returned = await svc.register("u@example.com", "password123", role)
        assert returned.role == role


# ── login ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens():
    repo = _make_repo()
    user = _make_user()
    repo.get_user_by_email.return_value = user
    repo.save_refresh_token.return_value = MagicMock()
    svc = _make_service(repo)

    access, refresh, returned = await svc.login("user@example.com", "password123")

    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert returned == user
    repo.update_last_login.assert_called_once_with(user.user_id)


@pytest.mark.asyncio
async def test_login_wrong_password_raises():
    repo = _make_repo()
    user = _make_user()
    repo.get_user_by_email.return_value = user
    svc = _make_service(repo)
    with pytest.raises(InvalidCredentialsError):
        await svc.login("user@example.com", "wrongpassword")


@pytest.mark.asyncio
async def test_login_unknown_email_raises():
    repo = _make_repo()
    repo.get_user_by_email.return_value = None
    svc = _make_service(repo)
    with pytest.raises(InvalidCredentialsError):
        await svc.login("ghost@example.com", "password123")


@pytest.mark.asyncio
async def test_login_inactive_user_raises():
    repo = _make_repo()
    user = _make_user(is_active=False)
    repo.get_user_by_email.return_value = user
    svc = _make_service(repo)
    with pytest.raises(InactiveUserError):
        await svc.login("user@example.com", "password123")


# ── refresh ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_valid_token_returns_new_tokens():
    repo = _make_repo()
    user = _make_user()
    raw_token = generate_refresh_token()
    token_hash = hash_token(raw_token)
    repo.get_active_refresh_token.return_value = _make_token_record(user.user_id, token_hash)
    repo.get_user_by_id.return_value = user
    repo.save_refresh_token.return_value = MagicMock()
    svc = _make_service(repo)

    new_access, new_refresh = await svc.refresh(str(user.user_id), raw_token)

    assert isinstance(new_access, str)
    assert isinstance(new_refresh, str)
    assert new_refresh != raw_token
    repo.revoke_refresh_token.assert_called_once()
    repo.save_refresh_token.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_invalid_token_raises():
    repo = _make_repo()
    user = _make_user()
    repo.get_active_refresh_token.return_value = None
    svc = _make_service(repo)
    with pytest.raises(InvalidRefreshTokenError):
        await svc.refresh(str(user.user_id), "invalid-token")


@pytest.mark.asyncio
async def test_refresh_invalid_user_id_raises():
    repo = _make_repo()
    svc = _make_service(repo)
    with pytest.raises(InvalidRefreshTokenError):
        await svc.refresh("not-a-uuid", "sometoken")


@pytest.mark.asyncio
async def test_refresh_inactive_user_raises():
    repo = _make_repo()
    user = _make_user(is_active=False)
    raw_token = generate_refresh_token()
    token_hash = hash_token(raw_token)
    repo.get_active_refresh_token.return_value = _make_token_record(user.user_id, token_hash)
    repo.get_user_by_id.return_value = user
    svc = _make_service(repo)
    with pytest.raises(InvalidRefreshTokenError):
        await svc.refresh(str(user.user_id), raw_token)


# ── logout ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_logout_revokes_token():
    repo = _make_repo()
    user = _make_user()
    svc = _make_service(repo)
    raw_token = generate_refresh_token()
    await svc.logout(str(user.user_id), raw_token)
    repo.revoke_refresh_token.assert_called_once()


@pytest.mark.asyncio
async def test_logout_invalid_user_id_does_not_raise():
    repo = _make_repo()
    svc = _make_service(repo)
    # Should silently ignore malformed user_id
    await svc.logout("not-a-uuid", "sometoken")
    repo.revoke_refresh_token.assert_not_called()


# ── change_password ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_change_password_success():
    repo = _make_repo()
    user = _make_user()
    repo.get_user_by_id.return_value = user
    svc = _make_service(repo)

    await svc.change_password(str(user.user_id), "password123", "NewPassword456!")

    repo.update_password.assert_called_once()
    repo.revoke_all_user_tokens.assert_called_once_with(user.user_id)


@pytest.mark.asyncio
async def test_change_password_wrong_current_raises():
    repo = _make_repo()
    user = _make_user()
    repo.get_user_by_id.return_value = user
    svc = _make_service(repo)
    with pytest.raises(InvalidCredentialsError):
        await svc.change_password(str(user.user_id), "wrongcurrent", "NewPassword456!")


@pytest.mark.asyncio
async def test_change_password_weak_new_raises():
    repo = _make_repo()
    svc = _make_service(repo)
    user = _make_user()
    with pytest.raises(WeakPasswordError):
        await svc.change_password(str(user.user_id), "password123", "short")


@pytest.mark.asyncio
async def test_change_password_user_not_found_raises():
    repo = _make_repo()
    repo.get_user_by_id.return_value = None
    svc = _make_service(repo)
    with pytest.raises(InvalidCredentialsError):
        await svc.change_password(str(uuid.uuid4()), "password123", "NewPassword456!")
