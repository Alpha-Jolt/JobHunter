# orchestration/services/mail_service.py

import httpx
from datetime import datetime
from uuid import uuid4
import logging

from orchestration.core.exceptions import (
    ApprovalRequiredError,
    DuplicateApplicationError,
    RateLimitError,
    JobError,
    MailSendError
)
from shared.models.application_record import ApplicationRecord
from shared.registries.job_registry import JobRegistry
from shared.registries.variant_registry import VariantRegistry
from shared.registries.application_log import ApplicationLog

logger = logging.getLogger(__name__)


class MailService:
    """HTTP client that calls Mail-Bridge to send job application emails."""

    def __init__(
        self,
        mail_bridge_url: str,
        mail_bridge_api_key: str,
        job_registry: JobRegistry,
        variant_registry: VariantRegistry,
        application_log: ApplicationLog,
        s3_client,  # boto3 s3 client for generating signed URLs
        max_applications_per_day: int = 10,
        min_seconds_between_sends: int = 30
    ):
        self.mail_bridge_url = mail_bridge_url
        self.mail_bridge_api_key = mail_bridge_api_key
        self.job_registry = job_registry
        self.variant_registry = variant_registry
        self.application_log = application_log
        self.s3_client = s3_client
        self.max_applications_per_day = max_applications_per_day
        self.min_seconds_between_sends = min_seconds_between_sends

    async def send_application(
        self,
        user_id: str,
        job_id: str,
        variant_id: str,
        user_name: str,
        user_email: str,
        user_phone: str,
        user_summary: str
    ) -> ApplicationRecord:
        """
        Send a job application email.

        All validation gates run here.
        Only after all gates pass does this call Mail-Bridge.
        """

        logger.info('send_application_started', extra={
            'user_id': user_id,
            'job_id': job_id,
            'variant_id': variant_id
        })

        # ─────────────────────────────────────────────────────────────────
        # GATE 1: Variant exists and is approved
        # ─────────────────────────────────────────────────────────────────

        try:
            variant = await self.variant_registry.get(variant_id)
        except Exception as e:
            logger.error('variant_fetch_failed', extra={'variant_id': variant_id, 'error': str(e)})
            raise JobError(f'Variant not found: {variant_id}')

        if variant.approval_status != 'approved':
            logger.warning('variant_not_approved', extra={
                'variant_id': variant_id,
                'status': variant.approval_status
            })
            raise ApprovalRequiredError(
                f'Variant {variant_id} must be approved before sending. '
                f'Current status: {variant.approval_status}'
            )

        # ─────────────────────────────────────────────────────────────────
        # GATE 2: Duplicate application check
        # ─────────────────────────────────────────────────────────────────

        already_applied = await self.application_log.has_user_applied_to_job(user_id, job_id)
        if already_applied:
            logger.warning('duplicate_application', extra={
                'user_id': user_id,
                'job_id': job_id
            })
            raise DuplicateApplicationError(
                f'User {user_id} has already applied to job {job_id}'
            )

        # ─────────────────────────────────────────────────────────────────
        # GATE 3: Daily send limit (10/day)
        # ─────────────────────────────────────────────────────────────────

        sent_today = await self.application_log.get_applications_sent_today(user_id)
        if len(sent_today) >= self.max_applications_per_day:
            logger.warning('daily_limit_exceeded', extra={
                'user_id': user_id,
                'count': len(sent_today),
                'limit': self.max_applications_per_day
            })
            raise RateLimitError(
                f'User {user_id} has reached daily limit of {self.max_applications_per_day} '
                f'applications. Try again tomorrow.'
            )

        # ─────────────────────────────────────────────────────────────────
        # GATE 4: Rate limit between sends (30 seconds)
        # ─────────────────────────────────────────────────────────────────

        if sent_today:
            last_send = sent_today[-1]  # most recent
            seconds_since_last = (datetime.utcnow() - last_send.sent_at).total_seconds()
            if seconds_since_last < self.min_seconds_between_sends:
                logger.warning('rate_limit_too_fast', extra={
                    'user_id': user_id,
                    'seconds_since_last': seconds_since_last,
                    'min_required': self.min_seconds_between_sends
                })
                raise RateLimitError(
                    f'Please wait {self.min_seconds_between_sends} seconds between sending '
                    f'applications. Last send was {seconds_since_last:.0f}s ago.'
                )

        # ─────────────────────────────────────────────────────────────────
        # GATE 5: Job exists, has apply_email, not closed
        # ─────────────────────────────────────────────────────────────────

        try:
            job = await self.job_registry.get(job_id)
        except Exception as e:
            logger.error('job_fetch_failed', extra={'job_id': job_id, 'error': str(e)})
            raise JobError(f'Job not found: {job_id}')

        if not job.apply_email:
            logger.error('job_no_apply_email', extra={'job_id': job_id})
            raise JobError(f'Job {job_id} has no contact email to send application to')

        if job.status == 'closed':
            logger.warning('job_closed', extra={'job_id': job_id})
            raise JobError(f'Job {job_id} is closed. Cannot apply.')

        # ─────────────────────────────────────────────────────────────────
        # PAYLOAD ASSEMBLY
        # ─────────────────────────────────────────────────────────────────

        logger.info('assembling_payload', extra={
            'user_id': user_id,
            'job_id': job_id
        })

        # Generate signed S3 URLs (15-minute expiry)
        resume_signed_url = self._generate_signed_url(
            variant.pdf_key,
            expires_in=900  # 15 minutes
        )
        cover_letter_signed_url = self._generate_signed_url(
            variant.cover_letter_id,
            expires_in=900
        )

        # Build context for email template
        context = {
            'user': {
                'name': user_name,
                'email': user_email,
                'phone': user_phone,
                'summary': user_summary
            },
            'job': {
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location
            }
        }

        # Build payload
        payload = {
            'to_email': job.apply_email,
            'template': 'standard',
            'context': context,
            'attachments': [
                {
                    'filename': f'{user_name.replace(" ", "_")}_Resume.pdf',
                    'signed_url': resume_signed_url
                },
                {
                    'filename': f'{user_name.replace(" ", "_")}_Cover_Letter.pdf',
                    'signed_url': cover_letter_signed_url
                }
            ]
        }

        # ─────────────────────────────────────────────────────────────────
        # CALL MAIL-BRIDGE
        # ─────────────────────────────────────────────────────────────────

        logger.info('calling_mail_bridge', extra={
            'to_email': job.apply_email,
            'user_id': user_id,
            'job_id': job_id
        })

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f'{self.mail_bridge_url}/api/mail/send',
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-API-Key': self.mail_bridge_api_key
                    }
                )

                if response.status_code != 200:
                    error_data = response.json()
                    error_code = error_data.get('error', {}).get('code', 'UNKNOWN')
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    logger.error('mail_bridge_error', extra={
                        'status_code': response.status_code,
                        'error_code': error_code,
                        'error_message': error_message
                    })
                    raise MailSendError(f'Mail-Bridge error: {error_code} - {error_message}')

                result = response.json()
                if not result.get('success'):
                    logger.error('mail_bridge_unsuccessful', extra=result)
                    raise MailSendError('Mail-Bridge returned success=false')

                message_id = result['message_id']
                sent_at = result['sent_at']

            except httpx.RequestError as e:
                logger.error('mail_bridge_connection_error', extra={
                    'url': self.mail_bridge_url,
                    'error': str(e)
                })
                raise MailSendError(f'Failed to reach Mail-Bridge: {str(e)}')

        # ─────────────────────────────────────────────────────────────────
        # RECORD APPLICATION (only after successful send)
        # ─────────────────────────────────────────────────────────────────

        logger.info('recording_application', extra={
            'user_id': user_id,
            'job_id': job_id,
            'message_id': message_id
        })

        application = ApplicationRecord(
            application_id=str(uuid4()),
            user_id=user_id,
            job_id=job_id,
            resume_variant_id=variant_id,
            cover_letter_id=variant.cover_letter_id,
            status='sent',
            sent_at=datetime.fromisoformat(sent_at),
            thread_id=message_id,
            email_subject=f'Application for {job.title}',
            reply_count=0,
            notes=None
        )

        await self.application_log.record_send(application)

        logger.info('application_sent', extra={
            'application_id': application.application_id,
            'user_id': user_id,
            'job_id': job_id,
            'message_id': message_id
        })

        return application

    def _generate_signed_url(self, s3_key: str, expires_in: int = 900) -> str:
        """Generate a time-limited signed URL for S3 object."""
        import os
        bucket = os.environ.get('S3_BUCKET', 'jobhunter-resumes')
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': s3_key
            },
            ExpiresIn=expires_in
        )

    async def get_application_status(self, application_id: str) -> ApplicationRecord:
        """Retrieve application status."""
        return await self.application_log.get(application_id)

    async def get_sent_today(self, user_id: str) -> list[ApplicationRecord]:
        """Get applications sent by user in last 24 hours."""
        return await self.application_log.get_applications_sent_today(user_id)
