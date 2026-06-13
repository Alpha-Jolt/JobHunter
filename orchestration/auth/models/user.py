"""User domain model and role enum."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class RoleEnum(str, Enum):
    HUNTER = "hunter"
    MENTOR = "mentor"
    RECRUITER = "recruiter"
    ADMIN = "admin"


@dataclass
class UserRecord:
    user_id: uuid.UUID
    email: str
    password_hash: str
    role: RoleEnum
    is_active: bool = True
    is_verified: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    verified_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
