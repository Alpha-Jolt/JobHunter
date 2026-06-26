"""Auth repository — PostgreSQL CRUD for users and refresh tokens."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import orchestration.db.models as _m
from orchestration.auth.models.tokens import RefreshTokenRecord
from orchestration.auth.models.user import RoleEnum, UserRecord


class UserAlreadyExistsError(Exception):
    """Raised when registering with a duplicate email."""


class UserNotFoundError(Exception):
    """Raised when a user lookup returns no result."""


def _row_to_user(row: _m.User) -> UserRecord:
    return UserRecord(
        user_id=row.user_id,
        email=row.email,
        password_hash=row.password_hash,
        role=RoleEnum(row.role),
        is_active=row.is_active,
        is_verified=row.is_verified,
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        verified_at=row.verified_at,
        last_login_at=row.last_login_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _row_to_token(row: _m.RefreshToken) -> RefreshTokenRecord:
    return RefreshTokenRecord(
        token_id=row.token_id,
        user_id=row.user_id,
        token_hash=row.token_hash,
        issued_at=row.issued_at,
        expires_at=row.expires_at,
        revoked=row.revoked,
        revoked_at=row.revoked_at,
    )


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Users ─────────────────────────────────────────────────────────────────

    async def create_user(
        self,
        email: str,
        password_hash: str,
        role: RoleEnum,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> UserRecord:
        """Insert a new user row.

        Raises:
            UserAlreadyExistsError: If email is already registered.
        """
        row = _m.User(
            user_id=uuid.uuid4(),
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role.value,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            raise UserAlreadyExistsError(f"Email already registered: {email}")
        return _row_to_user(row)

    async def get_user_by_email(self, email: str) -> Optional[UserRecord]:
        """Return user by email, or None if not found."""
        result = await self._session.execute(
            select(_m.User).where(_m.User.email == email.lower().strip())
        )
        row = result.scalar_one_or_none()
        return _row_to_user(row) if row else None

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserRecord]:
        """Return user by UUID, or None if not found."""
        result = await self._session.execute(
            select(_m.User).where(_m.User.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return _row_to_user(row) if row else None

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Stamp last_login_at for the given user."""
        await self._session.execute(
            update(_m.User)
            .where(_m.User.user_id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )

    async def update_password(self, user_id: uuid.UUID, new_hash: str) -> None:
        """Update password_hash for the given user."""
        await self._session.execute(
            update(_m.User)
            .where(_m.User.user_id == user_id)
            .values(password_hash=new_hash, updated_at=datetime.now(timezone.utc))
        )

    async def deactivate_user(self, user_id: uuid.UUID) -> None:
        """Set is_active=False for the given user."""
        await self._session.execute(
            update(_m.User)
            .where(_m.User.user_id == user_id)
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
        )

    async def update_role(self, user_id: uuid.UUID, role: RoleEnum) -> None:
        """Update user role (admin-only operation)."""
        await self._session.execute(
            update(_m.User)
            .where(_m.User.user_id == user_id)
            .values(role=role.value, updated_at=datetime.now(timezone.utc))
        )

    async def list_users(
        self,
        role: Optional[RoleEnum] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[UserRecord]:
        """List users with optional role filter."""
        q = select(_m.User).order_by(_m.User.created_at.desc()).limit(limit).offset(offset)
        if role:
            q = q.where(_m.User.role == role.value)
        result = await self._session.execute(q)
        return [_row_to_user(r) for r in result.scalars().all()]

    # ── Refresh Tokens ────────────────────────────────────────────────────────

    async def save_refresh_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshTokenRecord:
        """Persist a new (hashed) refresh token."""
        row = _m.RefreshToken(
            token_id=uuid.uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._session.add(row)
        await self._session.flush()
        return _row_to_token(row)

    async def get_active_refresh_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
    ) -> Optional[RefreshTokenRecord]:
        """Return a non-revoked, non-expired refresh token or None."""
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(_m.RefreshToken).where(
                _m.RefreshToken.user_id == user_id,
                _m.RefreshToken.token_hash == token_hash,
                _m.RefreshToken.revoked.is_(False),
                _m.RefreshToken.expires_at > now,
            )
        )
        row = result.scalar_one_or_none()
        return _row_to_token(row) if row else None

    async def get_active_refresh_token_by_hash(
        self,
        token_hash: str,
    ) -> Optional[RefreshTokenRecord]:
        """Return a non-revoked, non-expired refresh token by hash only."""
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(_m.RefreshToken).where(
                _m.RefreshToken.token_hash == token_hash,
                _m.RefreshToken.revoked.is_(False),
                _m.RefreshToken.expires_at > now,
            )
        )
        row = result.scalar_one_or_none()
        return _row_to_token(row) if row else None

    async def revoke_refresh_token(self, user_id: uuid.UUID, token_hash: str) -> None:
        """Mark a specific refresh token as revoked."""
        await self._session.execute(
            update(_m.RefreshToken)
            .where(
                _m.RefreshToken.user_id == user_id,
                _m.RefreshToken.token_hash == token_hash,
            )
            .values(revoked=True, revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revoke all refresh tokens for a user (logout-all)."""
        await self._session.execute(
            update(_m.RefreshToken)
            .where(_m.RefreshToken.user_id == user_id, _m.RefreshToken.revoked.is_(False))
            .values(revoked=True, revoked_at=datetime.now(timezone.utc))
        )
