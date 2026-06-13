"""Unit tests for auth/repository.py — mocked async DB session."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.models.tokens import RefreshTokenRecord
from orchestration.auth.repository import AuthRepository, UserAlreadyExistsError
import orchestration.db.models as _m


def _mock_user_row(
    user_id=None, email="test@example.com", role="hunter",
    is_active=True, is_verified=False,
):
    row = MagicMock(spec=_m.User)
    row.user_id = user_id or uuid.uuid4()
    row.email = email
    row.password_hash = "$argon2id$v=19$..."
    row.role = role
    row.is_active = is_active
    row.is_verified = is_verified
    row.first_name = None
    row.last_name = None
    row.phone = None
    row.verified_at = None
    row.last_login_at = None
    row.created_at = datetime.now(timezone.utc)
    row.updated_at = datetime.now(timezone.utc)
    return row


def _mock_token_row(user_id, token_hash, expires_at, revoked=False):
    row = MagicMock(spec=_m.RefreshToken)
    row.token_id = uuid.uuid4()
    row.user_id = user_id
    row.token_hash = token_hash
    row.issued_at = datetime.now(timezone.utc)
    row.expires_at = expires_at
    row.revoked = revoked
    row.revoked_at = None
    return row


def _make_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session


# ── create_user ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_user_returns_user_record():
    session = _make_session()
    repo = AuthRepository(session)
    with patch("orchestration.auth.repository._row_to_user") as mock_convert:
        mock_convert.return_value = UserRecord(
            user_id=uuid.uuid4(), email="test@example.com",
            password_hash="hash", role=RoleEnum.HUNTER,
        )
        result = await repo.create_user("test@example.com", "hash", RoleEnum.HUNTER)
    assert isinstance(result, UserRecord)
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_normalizes_email():
    session = _make_session()
    repo = AuthRepository(session)
    added_rows = []
    session.add.side_effect = lambda row: added_rows.append(row)
    with patch("orchestration.auth.repository._row_to_user", return_value=MagicMock()):
        await repo.create_user("  TEST@EXAMPLE.COM  ", "hash", RoleEnum.HUNTER)
    assert added_rows[0].email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user_raises_on_duplicate():
    from sqlalchemy.exc import IntegrityError
    session = _make_session()
    session.flush.side_effect = IntegrityError("duplicate", {}, None)
    session.rollback = AsyncMock()
    repo = AuthRepository(session)
    with pytest.raises(UserAlreadyExistsError):
        await repo.create_user("dup@example.com", "hash", RoleEnum.HUNTER)


@pytest.mark.asyncio
async def test_create_user_sets_role():
    session = _make_session()
    repo = AuthRepository(session)
    added_rows = []
    session.add.side_effect = lambda row: added_rows.append(row)
    with patch("orchestration.auth.repository._row_to_user", return_value=MagicMock()):
        await repo.create_user("m@example.com", "hash", RoleEnum.MENTOR)
    assert added_rows[0].role == "mentor"


# ── get_user_by_email ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_by_email_found():
    session = _make_session()
    row = _mock_user_row(email="found@example.com")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = row
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    user = await repo.get_user_by_email("found@example.com")
    assert user is not None
    assert user.email == "found@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    session = _make_session()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    user = await repo.get_user_by_email("nobody@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email_normalizes_input():
    session = _make_session()
    row = _mock_user_row(email="lower@example.com")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = row
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    user = await repo.get_user_by_email("  LOWER@EXAMPLE.COM  ")
    assert user is not None


# ── get_user_by_id ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_by_id_found():
    session = _make_session()
    uid = uuid.uuid4()
    row = _mock_user_row(user_id=uid)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = row
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    user = await repo.get_user_by_id(uid)
    assert user is not None
    assert user.user_id == uid


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    session = _make_session()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    user = await repo.get_user_by_id(uuid.uuid4())
    assert user is None


# ── save_refresh_token ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_refresh_token_returns_record():
    session = _make_session()
    repo = AuthRepository(session)
    uid = uuid.uuid4()
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    with patch("orchestration.auth.repository._row_to_token") as mock_convert:
        mock_convert.return_value = RefreshTokenRecord(
            token_id=uuid.uuid4(), user_id=uid, token_hash="hash",
            issued_at=datetime.now(timezone.utc), expires_at=expires,
        )
        record = await repo.save_refresh_token(uid, "hash", expires)
    assert isinstance(record, RefreshTokenRecord)
    session.add.assert_called_once()


# ── get_active_refresh_token ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_active_refresh_token_found():
    session = _make_session()
    uid = uuid.uuid4()
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    row = _mock_token_row(uid, "testhash", expires)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = row
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    record = await repo.get_active_refresh_token(uid, "testhash")
    assert record is not None
    assert record.token_hash == "testhash"


@pytest.mark.asyncio
async def test_get_active_refresh_token_not_found():
    session = _make_session()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    record = await repo.get_active_refresh_token(uuid.uuid4(), "notexist")
    assert record is None


# ── revoke / update helpers ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_revoke_refresh_token_executes():
    session = _make_session()
    repo = AuthRepository(session)
    await repo.revoke_refresh_token(uuid.uuid4(), "somehash")
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_revoke_all_user_tokens_executes():
    session = _make_session()
    repo = AuthRepository(session)
    await repo.revoke_all_user_tokens(uuid.uuid4())
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_last_login_executes():
    session = _make_session()
    repo = AuthRepository(session)
    await repo.update_last_login(uuid.uuid4())
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_password_executes():
    session = _make_session()
    repo = AuthRepository(session)
    await repo.update_password(uuid.uuid4(), "newhash")
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_user_executes():
    session = _make_session()
    repo = AuthRepository(session)
    await repo.deactivate_user(uuid.uuid4())
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_role_executes():
    session = _make_session()
    repo = AuthRepository(session)
    await repo.update_role(uuid.uuid4(), RoleEnum.ADMIN)
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_list_users_returns_list():
    session = _make_session()
    rows = [_mock_user_row(), _mock_user_row()]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = rows
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    users = await repo.list_users()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_list_users_with_role_filter():
    session = _make_session()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    session.execute.return_value = result_mock
    repo = AuthRepository(session)
    users = await repo.list_users(role=RoleEnum.ADMIN)
    assert users == []
