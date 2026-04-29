"""Cleaning pipeline orchestrator — IntermediateJob → CleanedJob."""

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from scraper.cleaning.date_cleaner import DateCleaner
from scraper.cleaning.location_cleaner import LocationCleaner
from scraper.cleaning.salary_cleaner import SalaryCleaner
from scraper.cleaning.text_cleaner import TextCleaner
from scraper.extraction.intermediate_schema import IntermediateJob
from scraper.logging_.logger import Logger

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"
    UNKNOWN = "unknown"


class RemoteType(str, Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"
    UNKNOWN = "unknown"


_JOB_TYPE_MAP = {
    "full time": JobType.FULL_TIME,
    "full-time": JobType.FULL_TIME,
    "fulltime": JobType.FULL_TIME,
    "part time": JobType.PART_TIME,
    "part-time": JobType.PART_TIME,
    "contract": JobType.CONTRACT,
    "freelance": JobType.CONTRACT,
    "internship": JobType.INTERNSHIP,
    "intern": JobType.INTERNSHIP,
    "temporary": JobType.TEMPORARY,
    "temp": JobType.TEMPORARY,
}

_REMOTE_MAP = {
    "remote": RemoteType.REMOTE,
    "work from home": RemoteType.REMOTE,
    "wfh": RemoteType.REMOTE,
    "hybrid": RemoteType.HYBRID,
    "onsite": RemoteType.ONSITE,
    "on-site": RemoteType.ONSITE,
    "in office": RemoteType.ONSITE,
}


class CleanedJob(BaseModel):
    """Cleaned and partially normalised job data."""

    title: str
    company_name: str

    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_raw: str = ""
    remote_type: RemoteType = RemoteType.UNKNOWN

    salary_min_inr: Optional[int] = None
    salary_max_inr: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_raw: str = ""

    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    experience_raw: str = ""

    job_type: JobType = JobType.UNKNOWN
    job_type_raw: str = ""
    posted_date: Optional[datetime] = None
    posted_date_raw: str = ""

    description: str = ""
    skills_required: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    apply_url: Optional[str] = None
    apply_email: Optional[str] = None
    company_domain: Optional[str] = None

    source: str
    external_id: str
    raw_url: str

    cleaning_timestamp: datetime = Field(default_factory=datetime.utcnow)
    cleaning_steps_applied: List[str] = Field(default_factory=list)


class CleanerPipeline:
    """Orchestrates all cleaning steps for a single IntermediateJob."""

    def __init__(self) -> None:
        self.logger = Logger.get_logger(__name__)

    async def clean(self, job: IntermediateJob) -> CleanedJob:
        """Apply all cleaning steps and return a CleanedJob."""
        steps: List[str] = []

        title = self._apply("title", lambda: TextCleaner.clean_field(job.title or ""), steps)
        company = self._apply(
            "company",
            lambda: TextCleaner.clean_field(job.company_name or ""),
            steps,
        )

        city, state = self._apply(
            "location",
            lambda: LocationCleaner.clean_location(job.location_raw),
            steps,
            default=(None, None),
        )
        remote_type = self._detect_remote(job.location_raw or "")

        sal_min, sal_max, sal_currency = self._apply(
            "salary",
            lambda: SalaryCleaner.clean_salary(job.salary_raw),
            steps,
            default=(None, None, None),
        )

        posted_date = self._apply(
            "date",
            lambda: DateCleaner.parse_posted_date(job.posted_date_raw),
            steps,
            default=None,
        )

        description = self._apply(
            "description",
            lambda: TextCleaner.clean_field(job.description or ""),
            steps,
        )

        skills = self._apply(
            "skills",
            lambda: TextCleaner.clean_list(job.skills_required_raw or []),
            steps,
            default=[],
        )

        benefits = self._apply(
            "benefits",
            lambda: TextCleaner.clean_list(job.benefits_raw or []),
            steps,
            default=[],
        )

        email = self._apply(
            "email",
            lambda: self._validate_email(job.apply_email_raw),
            steps,
            default=None,
        )

        exp_min, exp_max = self._parse_experience(job.experience_raw or "")
        job_type = self._parse_job_type(job.job_type_raw or "")

        return CleanedJob(
            title=title,
            company_name=company,
            location_city=city,
            location_state=state,
            location_raw=job.location_raw or "",
            remote_type=remote_type,
            salary_min_inr=sal_min,
            salary_max_inr=sal_max,
            salary_currency=sal_currency,
            salary_raw=job.salary_raw or "",
            experience_min_years=exp_min,
            experience_max_years=exp_max,
            experience_raw=job.experience_raw or "",
            job_type=job_type,
            job_type_raw=job.job_type_raw or "",
            posted_date=posted_date,
            posted_date_raw=job.posted_date_raw or "",
            description=description,
            skills_required=skills,
            benefits=benefits,
            apply_url=job.apply_url,
            apply_email=email,
            company_domain=job.company_domain,
            source=job.source,
            external_id=job.external_id,
            raw_url=job.raw_url,
            cleaning_steps_applied=steps,
        )

    def _apply(self, step_name: str, fn, steps: List[str], default=None):
        try:
            result = fn()
            steps.append(step_name)
            return result
        except Exception as exc:
            self.logger.warning(
                f"Cleaning step '{step_name}' failed — using default",
                extra_data={"error": str(exc)},
            )
            return default

    @staticmethod
    def _detect_remote(location: str) -> RemoteType:
        lower = location.lower()
        for kw, rtype in _REMOTE_MAP.items():
            if kw in lower:
                return rtype
        return RemoteType.UNKNOWN

    @staticmethod
    def _parse_job_type(raw: str) -> JobType:
        lower = raw.lower()
        for kw, jtype in _JOB_TYPE_MAP.items():
            if kw in lower:
                return jtype
        return JobType.UNKNOWN

    @staticmethod
    def _parse_experience(raw: str) -> tuple:
        """Extract (min_years, max_years) from strings like '3-5 years'."""
        import re  # noqa: PLC0415

        nums = re.findall(r"\d+", raw)
        if len(nums) >= 2:
            return int(nums[0]), int(nums[1])
        if len(nums) == 1:
            return None, int(nums[0])
        return None, None

    @staticmethod
    def _validate_email(email: Optional[str]) -> Optional[str]:
        if not email:
            return None
        return email.strip() if _EMAIL_RE.match(email.strip()) else None
