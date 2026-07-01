"""Auth service — register, login, refresh, logout, change_password."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from orchestration.auth.hashing import hash_password, verify_password, needs_rehash
from orchestration.auth.models.user import RoleEnum, UserRecord
from orchestration.auth.repository import AuthRepository, UserAlreadyExistsError  # noqa: F401
from orchestration.auth.tokens import (
    encode_access_token,
    generate_refresh_token,
    hash_token,
)

_EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
MIN_PASSWORD_LENGTH = 8


class AuthError(Exception):
    """Generic auth failure (wrong password, inactive user, etc.)."""


class InvalidCredentialsError(AuthError):
    """Raised on bad email/password combination."""


class InactiveUserError(AuthError):
    """Raised when a deactivated user attempts to log in."""


class WeakPasswordError(AuthError):
    """Raised when password does not meet requirements."""


class InvalidRefreshTokenError(AuthError):
    """Raised on invalid or expired refresh token."""


class AuthService:
    def __init__(
        self,
        repo: AuthRepository,
        jwt_secret: str,
        jwt_algorithm: str,
        access_expiry_minutes: int,
        refresh_expiry_days: int,
    ) -> None:
        self._repo = repo
        self._secret = jwt_secret
        self._algorithm = jwt_algorithm
        self._access_expiry = timedelta(minutes=access_expiry_minutes)
        self._refresh_expiry = timedelta(days=refresh_expiry_days)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _validate_password(self, password: str) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
            )

    def _validate_email(self, email: str) -> None:
        if not _EMAIL_RE.match(email):
            raise ValueError(f"Invalid email format: {email}")

    def _make_access_token(self, user: UserRecord) -> str:
        from opentelemetry import trace
        tracer = trace.get_tracer("jobhunter.orchestration")
        with tracer.start_as_current_span("Generate Access Token"):
            expiry = datetime.now(timezone.utc) + self._access_expiry
            return encode_access_token(
                user_id=str(user.user_id),
                role=user.role,
                secret=self._secret,
                algorithm=self._algorithm,
                expiry=expiry,
            )

    # ── Public API ────────────────────────────────────────────────────────────

    async def register(
        self,
        email: str,
        password: str,
        role: RoleEnum,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> tuple[str, str, UserRecord]:
        """Register a new user and return (access_token, refresh_token, user).

        Raises:
            ValueError: Invalid email format.
            WeakPasswordError: Password too short.
            UserAlreadyExistsError: Email already registered.
        """
        self._validate_email(email)
        self._validate_password(password)

        pw_hash = hash_password(password)
        user = await self._repo.create_user(
            email=email,
            password_hash=pw_hash,
            role=role,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        access_token = self._make_access_token(user)
        refresh_raw = generate_refresh_token()
        refresh_hash = hash_token(refresh_raw)
        expires_at = datetime.now(timezone.utc) + self._refresh_expiry
        await self._repo.save_refresh_token(user.user_id, refresh_hash, expires_at)

        return access_token, refresh_raw, user

    async def login(self, email: str, password: str) -> tuple[str, str, UserRecord]:
        """Authenticate and return (access_token, refresh_token, user).

        Raises:
            InvalidCredentialsError: Wrong email or password.
            InactiveUserError: Account deactivated.
        """
        from orchestration.core.metrics import login_total, login_failure_total
        from orchestration.core.spans import traced
        
        user = await self._repo.get_user_by_email(email)
        
        async with traced("Password Verification"):
            is_valid_pw = user and verify_password(password, user.password_hash)
            
        if not is_valid_pw:
            login_failure_total.add(1, {"reason": "invalid_creds"})
            raise InvalidCredentialsError("Invalid email or password")
            
        if not user.is_active:
            login_failure_total.add(1, {"reason": "inactive"})
            raise InactiveUserError("Account has been deactivated")

        # Rehash if argon2 params changed
        if needs_rehash(user.password_hash):
            new_hash = hash_password(password)
            await self._repo.update_password(user.user_id, new_hash)

        await self._repo.update_last_login(user.user_id)

        access_token = self._make_access_token(user)
        refresh_raw = generate_refresh_token()
        refresh_hash = hash_token(refresh_raw)
        expires_at = datetime.now(timezone.utc) + self._refresh_expiry
        await self._repo.save_refresh_token(user.user_id, refresh_hash, expires_at)

        login_total.add(1, {"result": "success"})
        return access_token, refresh_raw, user

    async def refresh(
        self,
        refresh_token_raw: str,
    ) -> tuple[str, str]:
        """Rotate refresh token and return (new_access_token, new_refresh_token).

        Raises:
            InvalidRefreshTokenError: Token not found, expired, or revoked.
        """
        from orchestration.core.spans import traced
        async with traced("Validate Refresh Token"):
            old_hash = hash_token(refresh_token_raw)
            token_rec = await self._repo.get_active_refresh_token_by_hash(old_hash)
            if not token_rec:
                raise InvalidRefreshTokenError("Refresh token is invalid, expired, or revoked")

            user_id = token_rec.user_id
            user = await self._repo.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidRefreshTokenError("User not found or inactive")

        # Atomic rotation: revoke old, issue new
        from orchestration.core.metrics import refresh_token_total
        async with traced("Refresh Token Rotation"):
            await self._repo.revoke_refresh_token(user_id, old_hash)
            new_refresh_raw = generate_refresh_token()
            new_refresh_hash = hash_token(new_refresh_raw)
            expires_at = datetime.now(timezone.utc) + self._refresh_expiry
            await self._repo.save_refresh_token(user_id, new_refresh_hash, expires_at)
    
            new_access = self._make_access_token(user)
            
        refresh_token_total.add(1)
        return new_access, new_refresh_raw

    async def logout(self, refresh_token_raw: str) -> None:
        """Revoke the given refresh token.

        Args:
            refresh_token_raw: Raw (unhashed) refresh token from cookie.
        """
        token_hash = hash_token(refresh_token_raw)
        token_rec = await self._repo.get_active_refresh_token_by_hash(token_hash)
        if token_rec:
            await self._repo.revoke_refresh_token(token_rec.user_id, token_hash)

    async def change_password(
        self,
        user_id_str: str,
        current_password: str,
        new_password: str,
    ) -> None:
        """Verify current password and set new one.

        Raises:
            InvalidCredentialsError: Current password is wrong.
            WeakPasswordError: New password too short.
        """
        self._validate_password(new_password)

        user_id = uuid.UUID(user_id_str)
        user = await self._repo.get_user_by_id(user_id)
        if not user or not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")

        new_hash = hash_password(new_password)
        await self._repo.update_password(user_id, new_hash)
        # Invalidate all existing sessions
        await self._repo.revoke_all_user_tokens(user_id)
