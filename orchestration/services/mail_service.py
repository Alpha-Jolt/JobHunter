# orchestration/services/mail_service.py

import logging
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from orchestration.core.exceptions import (
    ApprovalRequiredError,
    DuplicateApplicationError,
    RateLimitError,
    JobError,
    MailSendError,
)
from orchestration.services.mailbridge_client import MailBridgeClient, MailBridgeError
from shared.models.application_record import ApplicationRecord
from shared.registries.job_registry import JobRegistry
from shared.registries.variant_registry import VariantRegistry
from shared.registries.application_log import ApplicationLog

logger = logging.getLogger(__name__)


class MailService:
    """Orchestrates job application email sending via Mail-Bridge v2.

    Credential resolution is per-user: each user connects their own Gmail (or
    SMTP) account in Mail-Bridge.  The resulting ``credential_id`` UUID is stored
    in ``user_mail_credentials`` and looked up here at send time — there is no
    single workspace-wide credential UUID in the environment.
    """

    def __init__(
        self,
        mailbridge_client: MailBridgeClient,
        job_registry: JobRegistry,
        variant_registry: VariantRegistry,
        application_log: ApplicationLog,
        db_session: AsyncSession,
        s3_client,
        max_applications_per_day: int = 10,
        min_seconds_between_sends: int = 30,
        minio_bucket: str = "jobhunter-resumes",
    ) -> None:
        self._client = mailbridge_client
        self._job_registry = job_registry
        self._variant_registry = variant_registry
        self._application_log = application_log
        self._session = db_session
        self._s3_client = s3_client
        self._max_per_day = max_applications_per_day
        self._min_gap = min_seconds_between_sends
        self._bucket = minio_bucket

    # ── credential lookup ─────────────────────────────────────────────────────

    async def _get_mailbridge_credential_id(self, user_id: str) -> str:
        """Return the Mail-Bridge credential_id for a user.

        Raises:
            MailSendError: If the user has no active mail credential configured.
        """
        import orchestration.db.models as _m

        result = await self._session.execute(
            select(_m.UserMailCredential).where(
                _m.UserMailCredential.user_id == user_id,
                _m.UserMailCredential.is_active.is_(True),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise MailSendError(
                f"User {user_id} has no connected mail account. "
                "Connect a Gmail or SMTP account in Settings → Mail."
            )
        return str(row.mailbridge_credential_id)

    # ── signed URL helpers ────────────────────────────────────────────────────

    def _presigned_url(self, s3_key: str, expires_in: int = 900) -> str:
        """Generate a time-limited presigned URL for a MinIO object."""
        return self._s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": s3_key},
            ExpiresIn=expires_in,
        )

    # ── store mailbridge_email_id after send ──────────────────────────────────

    async def _store_mailbridge_email_id(
        self, application_id: str, email_id: str
    ) -> None:
        """Persist the Mail-Bridge email_id against the application record."""
        import orchestration.db.models as _m
        from sqlalchemy import update

        await self._session.execute(
            update(_m.ApplicationLog)
            .where(_m.ApplicationLog.application_id == application_id)
            .values(mailbridge_email_id=email_id)
        )

    # ── main send method ──────────────────────────────────────────────────────

    async def send_application(
        self,
        user_id: str,
        job_id: str,
        variant_id: str,
        user_name: str,
        user_email: str,
        user_phone: str,
        user_summary: str,
    ) -> ApplicationRecord:
        """Send a job application email through Mail-Bridge.

        Runs all validation gates before calling Mail-Bridge.
        Records the application only after a successful send.

        Returns:
            The persisted ApplicationRecord.
        """

        logger.info(
            "send_application_started",
            extra={"user_id": user_id, "job_id": job_id, "variant_id": variant_id},
        )

        # ── GATE 1: variant approved ──────────────────────────────────────────
        try:
            variant = await self._variant_registry.get(variant_id)
        except Exception as exc:
            logger.error(
                "variant_fetch_failed",
                extra={"variant_id": variant_id, "error": str(exc)},
            )
            raise JobError(f"Variant not found: {variant_id}")

        if variant.approval_status != "approved":
            logger.warning(
                "variant_not_approved",
                extra={"variant_id": variant_id, "status": variant.approval_status},
            )
            raise ApprovalRequiredError(
                f"Variant {variant_id} must be approved before sending. "
                f"Current status: {variant.approval_status}"
            )

        # ── GATE 2: duplicate application ─────────────────────────────────────
        if await self._application_log.has_user_applied_to_job(user_id, job_id):
            logger.warning(
                "duplicate_application",
                extra={"user_id": user_id, "job_id": job_id},
            )
            raise DuplicateApplicationError(
                f"User {user_id} has already applied to job {job_id}"
            )

        # ── GATE 3: daily send limit ──────────────────────────────────────────
        sent_today = await self._application_log.get_applications_sent_today(user_id)
        if len(sent_today) >= self._max_per_day:
            logger.warning(
                "daily_limit_exceeded",
                extra={
                    "user_id": user_id,
                    "count": len(sent_today),
                    "limit": self._max_per_day,
                },
            )
            raise RateLimitError(
                f"User {user_id} has reached daily limit of {self._max_per_day} "
                "applications. Try again tomorrow."
            )

        # ── GATE 4: minimum gap between sends ─────────────────────────────────
        if sent_today:
            last_send = sent_today[-1]
            seconds_ago = (
                datetime.now(timezone.utc) - last_send.sent_at
            ).total_seconds()
            if seconds_ago < self._min_gap:
                logger.warning(
                    "rate_limit_too_fast",
                    extra={
                        "user_id": user_id,
                        "seconds_since_last": seconds_ago,
                        "min_required": self._min_gap,
                    },
                )
                raise RateLimitError(
                    f"Please wait {self._min_gap} seconds between applications. "
                    f"Last send was {seconds_ago:.0f}s ago."
                )

        # ── GATE 5: job exists, has apply_email, not closed ───────────────────
        try:
            job = await self._job_registry.get(job_id)
        except Exception as exc:
            logger.error("job_fetch_failed", extra={"job_id": job_id, "error": str(exc)})
            raise JobError(f"Job not found: {job_id}")

        if not job.apply_email:
            raise JobError(f"Job {job_id} has no contact email")
        if job.status == "closed":
            raise JobError(f"Job {job_id} is closed")

        # ── GATE 6: user has a connected mail account ─────────────────────────
        credential_id = await self._get_mailbridge_credential_id(user_id)

        # ── PAYLOAD ASSEMBLY ──────────────────────────────────────────────────
        logger.info(
            "assembling_payload",
            extra={"user_id": user_id, "job_id": job_id},
        )

        # Generate presigned URLs (15-min) — Mail-Bridge fetches the actual file
        resume_url = self._presigned_url(variant.pdf_key, expires_in=900)
        cover_letter_url = self._presigned_url(
            variant.cover_letter_key or variant.cover_letter_id, expires_in=900
        )

        safe_name = user_name.replace(" ", "_")

        # ── CALL MAIL-BRIDGE ──────────────────────────────────────────────────
        logger.info(
            "calling_mail_bridge",
            extra={"to_email": job.apply_email, "user_id": user_id, "job_id": job_id},
        )

        try:
            result = await self._client.send_email(
                credential_id=credential_id,
                to_email=job.apply_email,
                subject=f"Application for {job.title} at {job.company_name}",
                html=(
                    f"<p>Dear Hiring Manager,</p>"
                    f"<p>I am writing to apply for the <strong>{job.title}</strong> "
                    f"position at <strong>{job.company_name}</strong>. "
                    f"Please find my resume and cover letter attached.</p>"
                    f"<p>Best regards,<br>{user_name}</p>"
                ),
                variables={
                    "candidate_name": user_name,
                    "job_title": job.title,
                    "company_name": job.company_name,
                },
                attachments=[
                    {"filename": f"{safe_name}_Resume.pdf", "url": resume_url},
                    {"filename": f"{safe_name}_Cover_Letter.pdf", "url": cover_letter_url},
                ],
            )
        except MailBridgeError as exc:
            logger.error(
                "mail_bridge_send_failed",
                extra={"code": exc.code, "message": exc.message, "status": exc.status},
            )
            raise MailSendError(f"Mail-Bridge error {exc.code}: {exc.message}")

        email_id: str = result.get("email_id", "")

        # ── RECORD APPLICATION ────────────────────────────────────────────────
        application = ApplicationRecord(
            application_id=str(uuid4()),
            user_id=user_id,
            job_id=job_id,
            resume_variant_id=variant_id,
            cover_letter_id=getattr(variant, "cover_letter_id", None),
            status="sent",
            sent_at=datetime.now(timezone.utc),
            thread_id=email_id,
            email_subject=f"Application for {job.title}",
            reply_count=0,
            notes=None,
        )
        await self._application_log.record_send(application)

        # Persist the Mail-Bridge email_id for webhook tracking
        if email_id:
            await self._store_mailbridge_email_id(application.application_id, email_id)

        logger.info(
            "application_sent",
            extra={
                "application_id": application.application_id,
                "user_id": user_id,
                "job_id": job_id,
                "email_id": email_id,
            },
        )
        return application

    # ── batch outreach ────────────────────────────────────────────────────────

    async def send_outreach_batch(
        self,
        user_id: str,
        candidates: list[dict],
        template_id: str | None = None,
    ) -> dict:
        """Send outreach emails to a list of candidates.

        Each item in ``candidates`` must have ``email``, ``name``, ``job_title``.
        Splits automatically if the list exceeds 100 (Mail-Bridge batch limit).

        Returns:
            ``{"queued": N, "email_ids": [...]}``
        """
        credential_id = await self._get_mailbridge_credential_id(user_id)

        all_email_ids: list[str] = []
        chunk_size = 100

        for i in range(0, len(candidates), chunk_size):
            chunk = candidates[i : i + chunk_size]
            emails = [
                {
                    "credential_id": credential_id,
                    "to_email": c["email"],
                    "template_id": template_id,
                    "variables": {
                        "candidate_name": c["name"],
                        "job_title": c["job_title"],
                    },
                }
                for c in chunk
            ]
            try:
                result = await self._client.send_batch(emails)
                all_email_ids.extend(result.get("email_ids", []))
            except MailBridgeError as exc:
                logger.error(
                    "batch_send_failed",
                    extra={"code": exc.code, "chunk_start": i},
                )
                raise MailSendError(f"Batch send failed: {exc.code}")

        return {"queued": len(all_email_ids), "email_ids": all_email_ids}

    # ── scheduled follow-up ───────────────────────────────────────────────────

    async def schedule_follow_up(
        self,
        user_id: str,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        delay_days: int = 3,
        template_id: str | None = None,
    ) -> dict:
        """Schedule a follow-up email after ``delay_days`` days.

        Returns:
            ``{"scheduled_id": "...", "scheduled_at": "..."}``
        """
        credential_id = await self._get_mailbridge_credential_id(user_id)
        send_at = (
            datetime.now(timezone.utc) + timedelta(days=delay_days)
        ).isoformat()

        payload: dict = {
            "credential_id": credential_id,
            "to_email": candidate_email,
            "scheduled_at": send_at,
            "variables": {
                "candidate_name": candidate_name,
                "job_title": job_title,
                "days_since": str(delay_days),
            },
        }
        if template_id:
            payload["template_id"] = template_id
        else:
            payload["subject"] = f"Following up on my application for {job_title}"
            payload["html"] = (
                f"<p>Dear Hiring Team,</p>"
                f"<p>I wanted to follow up on my application for <strong>{job_title}</strong> "
                f"submitted {delay_days} days ago. I remain very interested.</p>"
                f"<p>Best regards,<br>{candidate_name}</p>"
            )

        try:
            return await self._client.schedule_email(payload)
        except MailBridgeError as exc:
            raise MailSendError(f"Schedule failed: {exc.code}")

    async def cancel_follow_up(self, scheduled_id: str) -> None:
        """Cancel a pending scheduled follow-up email."""
        try:
            await self._client.cancel_schedule(scheduled_id)
        except MailBridgeError as exc:
            raise MailSendError(f"Cancel failed: {exc.code}")

    # ── read helpers ──────────────────────────────────────────────────────────

    async def get_application_status(
        self, application_id: str
    ) -> ApplicationRecord:
        """Retrieve an application by ID."""
        import uuid
        return await self._application_log.get(uuid.UUID(application_id))

    async def get_sent_today(self, user_id: str) -> list[ApplicationRecord]:
        """Return applications sent by a user in the last 24 hours."""
        return await self._application_log.get_applications_sent_today(user_id)
