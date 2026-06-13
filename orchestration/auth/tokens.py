"""JWT encoding/decoding and refresh token utilities."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from jose import JWTError, jwt

from orchestration.auth.models.tokens import AccessTokenPayload
from orchestration.auth.models.user import RoleEnum


class TokenError(Exception):
    """Raised when a token cannot be decoded or is invalid."""


class TokenExpiredError(TokenError):
    """Raised when a JWT has expired."""


def encode_access_token(
    user_id: str,
    role: RoleEnum,
    secret: str,
    algorithm: str,
    expiry: datetime,
) -> str:
    """Encode a signed JWT access token.

    Args:
        user_id: UUID string of the authenticated user.
        role: User's role.
        secret: JWT signing secret (≥32 chars).
        algorithm: Signing algorithm (e.g. HS256).
        expiry: Token expiry datetime (UTC).

    Returns:
        Signed JWT string.
    """
    payload: dict[str, Any] = {
        "sub": user_id,
        "role": role.value,
        "exp": expiry,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(
    token: str,
    secret: str,
    algorithm: str,
) -> AccessTokenPayload:
    """Decode and validate a JWT access token.

    Args:
        token: JWT string.
        secret: JWT signing secret.
        algorithm: Expected signing algorithm.

    Returns:
        AccessTokenPayload dataclass.

    Raises:
        TokenExpiredError: If the token has expired.
        TokenError: If the token is malformed or invalid.
    """
    try:
        data = jwt.decode(token, secret, algorithms=[algorithm])
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredError("Access token has expired") from exc
        raise TokenError(f"Invalid token: {exc}") from exc

    return AccessTokenPayload(
        sub=data["sub"],
        role=RoleEnum(data["role"]),
        exp=datetime.fromtimestamp(data["exp"], tz=timezone.utc),
        iat=datetime.fromtimestamp(data["iat"], tz=timezone.utc),
        jti=data.get("jti", ""),
    )


def generate_refresh_token() -> str:
    """Generate a cryptographically secure opaque refresh token.

    Returns:
        URL-safe random token string (32 bytes = 43 chars base64url).
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """SHA-256 hash a token for safe storage.

    Args:
        token: Raw token string.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    return hashlib.sha256(token.encode()).hexdigest()
