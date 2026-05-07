# orchestration/api/routes/mail.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
import logging

from orchestration.services.mail_service import MailService
from orchestration.api.dependencies import get_mail_service
from orchestration.core.exceptions import (
    ApprovalRequiredError,
    DuplicateApplicationError,
    RateLimitError,
    JobError,
    MailSendError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mail", tags=["mail"])


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────

class SendApplicationRequest(BaseModel):
    user_id: str
    job_id: str
    variant_id: str
    user_name: str
    user_email: EmailStr
    user_phone: str
    user_summary: str


class SendApplicationResponse(BaseModel):
    success: bool
    application_id: str
    message_id: str
    sent_at: str


class ApplicationStatusResponse(BaseModel):
    application_id: str
    user_id: str
    job_id: str
    status: str
    sent_at: str
    reply_count: int


class SentTodayResponse(BaseModel):
    count: int
    applications: list[ApplicationStatusResponse]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/send", response_model=SendApplicationResponse)
async def send_application(
    request: SendApplicationRequest,
    mail_service: MailService = Depends(get_mail_service)
) -> SendApplicationResponse:
    """
    Send a job application email.

    All validation gates run in mail_service.send_application().
    Returns 400 if any gate fails (approval, duplicate, rate limit, job).
    """
    try:
        application = await mail_service.send_application(
            user_id=request.user_id,
            job_id=request.job_id,
            variant_id=request.variant_id,
            user_name=request.user_name,
            user_email=request.user_email,
            user_phone=request.user_phone,
            user_summary=request.user_summary
        )

        return SendApplicationResponse(
            success=True,
            application_id=str(application.application_id),
            message_id=application.thread_id,
            sent_at=application.sent_at.isoformat()
        )

    except ApprovalRequiredError as e:
        logger.warning('approval_required', extra={'error': str(e)})
        raise HTTPException(
            status_code=400,
            detail={'code': 'APPROVAL_REQUIRED', 'message': str(e)}
        )

    except DuplicateApplicationError as e:
        logger.warning('duplicate_application', extra={'error': str(e)})
        raise HTTPException(
            status_code=409,
            detail={'code': 'DUPLICATE_APPLICATION', 'message': str(e)}
        )

    except RateLimitError as e:
        logger.warning('rate_limit', extra={'error': str(e)})
        raise HTTPException(
            status_code=429,
            detail={'code': 'RATE_LIMIT', 'message': str(e)}
        )

    except JobError as e:
        logger.error('job_error', extra={'error': str(e)})
        raise HTTPException(
            status_code=400,
            detail={'code': 'JOB_ERROR', 'message': str(e)}
        )

    except MailSendError as e:
        logger.error('mail_send_error', extra={'error': str(e)})
        raise HTTPException(
            status_code=500,
            detail={'code': 'MAIL_SEND_ERROR', 'message': str(e)}
        )

    except Exception as e:
        logger.error('unexpected_error', extra={'error': str(e), 'type': type(e).__name__})
        raise HTTPException(
            status_code=500,
            detail={'code': 'INTERNAL_ERROR', 'message': 'An unexpected error occurred'}
        )


@router.get("/status/{application_id}", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: str,
    mail_service: MailService = Depends(get_mail_service)
) -> ApplicationStatusResponse:
    """Get the status of a sent application."""
    try:
        application = await mail_service.get_application_status(application_id)
        return ApplicationStatusResponse(
            application_id=str(application.application_id),
            user_id=application.user_id,
            job_id=application.job_id,
            status=application.status,
            sent_at=application.sent_at.isoformat(),
            reply_count=application.reply_count
        )
    except Exception as e:
        logger.error('get_status_error', extra={'application_id': application_id, 'error': str(e)})
        raise HTTPException(
            status_code=404,
            detail={'code': 'NOT_FOUND', 'message': f'Application {application_id} not found'}
        )


@router.get("/sent-today/{user_id}", response_model=SentTodayResponse)
async def get_sent_today(
    user_id: str,
    mail_service: MailService = Depends(get_mail_service)
) -> SentTodayResponse:
    """Get all applications sent by user in the last 24 hours."""
    try:
        applications = await mail_service.get_sent_today(user_id)
        return SentTodayResponse(
            count=len(applications),
            applications=[
                ApplicationStatusResponse(
                    application_id=str(app.application_id),
                    user_id=app.user_id,
                    job_id=app.job_id,
                    status=app.status,
                    sent_at=app.sent_at.isoformat(),
                    reply_count=app.reply_count
                )
                for app in applications
            ]
        )
    except Exception as e:
        logger.error('get_sent_today_error', extra={'user_id': user_id, 'error': str(e)})
        raise HTTPException(
            status_code=500,
            detail={'code': 'INTERNAL_ERROR', 'message': 'Failed to retrieve sent applications'}
        )
