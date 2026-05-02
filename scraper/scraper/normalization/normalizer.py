"""Map CleanedJob → CanonicalJob with scoring and hashing."""

import hashlib
from datetime import datetime, timezone
from typing import Optional

from scraper.cleaning.cleaner_pipeline import CleanedJob
from scraper.normalization.canonical_schema import CanonicalJob

_RELIABLE_SOURCES = {"indeed", "naukri"}

_COMPLETENESS_FIELDS = [
    "title",
    "company_name",
    "description",
    "location_city",
    "salary_min_inr",
    "experience_min_years",
    "job_type",
    "apply_url",
]


class JobNormalizer:
    """Convert CleanedJob to CanonicalJob."""

    def normalize(self, job: CleanedJob) -> CanonicalJob:
        """Produce a CanonicalJob from a CleanedJob."""
        content_hash = self._content_hash(job)
        url_hash = hashlib.sha256(job.raw_url.encode()).hexdigest()[:16]

        apply_method = "email" if job.apply_email else ("url" if job.apply_url else "unknown")

        posted_days_ago: Optional[int] = None
        if job.posted_date:
            posted = job.posted_date
            if posted.tzinfo is None:
                posted = posted.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - posted
            posted_days_ago = max(0, delta.days)

        completeness = self._calculate_completeness(job)
        confidence = self._calculate_confidence(job)

        return CanonicalJob(
            source=job.source,
            external_id=job.external_id,
            source_url=job.raw_url,
            title=job.title,
            company_name=job.company_name,
            company_domain=job.company_domain,
            description=job.description,
            location_city=job.location_city,
            location_state=job.location_state,
            remote_type=job.remote_type.value,
            salary_min=job.salary_min_inr,
            salary_max=job.salary_max_inr,
            salary_currency=job.salary_currency,
            experience_min=job.experience_min_years,
            experience_max=job.experience_max_years,
            job_type=job.job_type.value,
            skills_required=job.skills_required,
            benefits=job.benefits,
            apply_url=job.apply_url,
            apply_email=job.apply_email,
            apply_method=apply_method,
            posted_at=job.posted_date,
            posted_days_ago=posted_days_ago,
            completeness_score=completeness,
            confidence_score=confidence,
            content_hash=content_hash,
            url_hash=url_hash,
        )

    def _calculate_completeness(self, job: CleanedJob) -> float:
        filled = sum(
            1 for f in _COMPLETENESS_FIELDS if getattr(job, f, None) not in (None, "", "unknown")
        )
        return round(filled / len(_COMPLETENESS_FIELDS), 2)

    def _calculate_confidence(self, job: CleanedJob) -> float:
        score = 0.0
        if job.salary_min_inr or job.salary_max_inr:
            score += 1.0
        if job.experience_min_years is not None or job.experience_max_years is not None:
            score += 1.0
        desc_len = len(job.description or "")
        if desc_len > 500:
            score += 1.0
        elif desc_len > 200:
            score += 0.5
        if job.source in _RELIABLE_SOURCES:
            score += 1.0
        else:
            score += 0.5
        if job.apply_email:
            score += 0.5
        if job.company_domain:
            score += 0.5
        return round(min(score / 5.0, 1.0), 2)

    @staticmethod
    def _content_hash(job: CleanedJob) -> str:
        raw = f"{job.title}|{job.company_name}|{job.location_raw}".lower()
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
