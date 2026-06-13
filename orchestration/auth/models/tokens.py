"""Token payload dataclasses."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from orchestration.auth.models.user import RoleEnum


@dataclass
class AccessTokenPayload:
    sub: str          # user_id (UUID string)
    role: RoleEnum
    exp: datetime
    iat: datetime
    jti: str = ""     # optional token id


@dataclass
class RefreshTokenRecord:
    token_id: uuid.UUID
    user_id: uuid.UUID
    token_hash: str
    issued_at: datetime
    expires_at: datetime
    revoked: bool = False
    revoked_at: datetime | None = None
