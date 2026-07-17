# orchestration/api/routes/mail_credentials.py

"""Mail credential management routes.

Lets a JobHunter user connect their Gmail (or SMTP) account via Mail-Bridge.
The OAuth flow is:
  1. User calls GET /api/mail/credentials/connect/gmail
     → JobHunter proxies to Mail-Bridge and returns the Google consent URL
  2. After OAuth, Mail-Bridge calls its own callback URL
  3. User tells JobHunter the credential_id (from Mail-Bridge dashboard) via
     POST /api/mail/credentials, which stores it in user_mail_credentials

For production, step 2 can be replaced by a direct OAuth callback route that
auto-stores the credential_id — left as a future enhancement.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from orchestration.auth.dependencies import require_role
from orchestration.auth.models.user import RoleEnum
from orchestration.api.dependencies import get_db_session, get_settings
from orchestration.api.config import Settings
from orchestration.services.mailbridge_client import MailBridgeClient, MailBridgeError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mail/credentials", tags=["mail-credentials"])


# ── request / response models ─────────────────────────────────────────────────

class SaveCredentialRequest(BaseModel):
    mailbridge_credential_id: UUID
    from_email: EmailStr
    provider_type: str = "gmail"


class CredentialResponse(BaseModel):
    mailbridge_credential_id: UUID
    from_email: str
    provider_type: str
    is_active: bool


# ── helpers ───────────────────────────────────────────────────────────────────

async def _get_client(settings: Settings) -> MailBridgeClient:
    return MailBridgeClient(
        base_url=settings.mail.mail_bridge_url,
        api_key=settings.mail.mail_bridge_api_key,
    )


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=CredentialResponse | None,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def get_credential(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Return the user's current mail credential, or null if not connected."""
    import orchestration.db.models as _m

    result = await session.execute(
        select(_m.UserMailCredential).where(
            _m.UserMailCredential.user_id == user_id,
            _m.UserMailCredential.is_active.is_(True),
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        return None
    return CredentialResponse(
        mailbridge_credential_id=row.mailbridge_credential_id,
        from_email=row.from_email,
        provider_type=row.provider_type,
        is_active=row.is_active,
    )


@router.post(
    "/",
    response_model=CredentialResponse,
    status_code=201,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def save_credential(
    user_id: str,
    body: SaveCredentialRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Store (or replace) a Mail-Bridge credential_id for this user.

    The user connects their Gmail via the Mail-Bridge webapp at
    ``app.myjobhunter.in``, then pastes / the system stores the returned
    ``credential_id`` here.
    """
    import orchestration.db.models as _m
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    stmt = (
        pg_insert(_m.UserMailCredential)
        .values(
            user_id=user_id,
            mailbridge_credential_id=body.mailbridge_credential_id,
            from_email=body.from_email,
            provider_type=body.provider_type,
            is_active=True,
        )
        .on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "mailbridge_credential_id": body.mailbridge_credential_id,
                "from_email": body.from_email,
                "provider_type": body.provider_type,
                "is_active": True,
            },
        )
    )
    await session.execute(stmt)

    logger.info(
        "mail_credential_saved",
        extra={"user_id": user_id, "from_email": body.from_email},
    )
    return CredentialResponse(
        mailbridge_credential_id=body.mailbridge_credential_id,
        from_email=body.from_email,
        provider_type=body.provider_type,
        is_active=True,
    )


@router.delete(
    "/",
    status_code=200,
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def disconnect_credential(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Mark the user's mail credential as inactive (disconnect)."""
    import orchestration.db.models as _m
    from sqlalchemy import update

    await session.execute(
        update(_m.UserMailCredential)
        .where(_m.UserMailCredential.user_id == user_id)
        .values(is_active=False)
    )
    return {"success": True}


@router.get(
    "/list-mailbridge",
    dependencies=[Depends(require_role(RoleEnum.HUNTER, RoleEnum.ADMIN))],
)
async def list_mailbridge_credentials(
    settings: Settings = Depends(get_settings),
):
    """Proxy GET /api/credentials/ on Mail-Bridge.

    Lets the frontend show available Gmail accounts from Mail-Bridge
    so the user can pick which credential_id to associate.
    """
    client = await _get_client(settings)
    try:
        return await client.list_credentials()
    except MailBridgeError as exc:
        raise HTTPException(
            status_code=exc.status or 502,
            detail={"code": exc.code, "message": exc.message},
        )
