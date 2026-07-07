"""Job cleaner pipeline for career page extracted jobs."""

import logging
import os
import re
from typing import List, Optional, Tuple

import yaml

from scraper.cleaning.text_cleaner import TextCleaner
from scraper.cleaning.location_cleaner import LocationCleaner
from scraper.cleaning.salary_cleaner import SalaryCleaner

logger = logging.getLogger(__name__)

# --- Task 1: Title garbage validation ----------------------------------------

# Navigation labels that are ALL_CAPS should be rejected
_ALL_CAPS_RE = re.compile(r"^[A-Z0-9\s\-&/]+$")

# Common navigation / site-structure labels (case-insensitive, full-string match)
_NAV_TITLE_RE = re.compile(
    r"^(contact(\s+us)?|careers?|apply(\s+(now|here))?|jobs?|"
    r"hiring|join\s+us|open\s+positions?|current\s+openings?|"
    r"home|about(\s+us)?|our\s+team|team|people|menu|search|"
    r"login|sign\s+in|register|submit|back|next|view\s+all|"
    r"work\s+with\s+us|our\s+impact|news(\s+&?\s+media)?|"
    r"publications?|resources?|registry|admissions?|naac|"
    r"privacy(\s+policy)?|press(\s+kit)?|investors?|partner)$",
    re.IGNORECASE,
)

_MIN_TITLE_LENGTH = 5
_MAX_TITLE_LENGTH = 120  # reject description-length strings extracted as titles


def _is_garbage_title(title: str) -> bool:
    """Return True if the title is a navigation/breadcrumb label, not a real job title.

    Rejects:
    - Titles that are ALL_CAPS (navigation pattern)
    - Titles matching known navigation label patterns
    - Titles shorter than MIN_TITLE_LENGTH characters

    Args:
        title: Cleaned job title string.

    Returns:
        True if title should be rejected.
    """
    if not title:
        return True
    stripped = title.strip()
    if len(stripped) < _MIN_TITLE_LENGTH:
        return True
    if len(stripped) > _MAX_TITLE_LENGTH:
        return True
    if _ALL_CAPS_RE.match(stripped):
        return True
    if _NAV_TITLE_RE.match(stripped):
        return True
    return False


# --- Task 2: Email extraction from job descriptions --------------------------

# Contextual email extraction patterns (high-confidence proximity signals)
_DESCRIPTION_EMAIL_PATTERNS = [
    re.compile(
        r"send\s+(?:your\s+)?(?:cv|resume|application)(?:\s+to)?\s+"
        r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
        re.IGNORECASE,
    ),
    re.compile(
        r"apply\s+(?:at|to)\s+"
        r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:email|mail|contact|reach|write)\s+(?:us\s+)?(?:at|to)?\s*:?\s*"
        r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
        re.IGNORECASE,
    ),
    # High-signal prefix patterns — HR/career local parts anywhere in text
    re.compile(
        r"\b((?:careers?|hr|jobs?|recruitment|talent|hiring|people|"
        r"staffing|apply|applications?)@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
        re.IGNORECASE,
    ),
]

_EMAIL_VALIDATE_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

_FREE_WEBMAIL = frozenset([
    "gmail.com", "yahoo.com", "yahoo.co.in", "hotmail.com", "rediffmail.com",
    "outlook.com", "ymail.com", "live.com", "aol.com", "protonmail.com",
])


def extract_emails_from_description(description: str) -> List[str]:
    """Extract apply email addresses from job description text.

    Uses contextual proximity patterns — never guesses, only extracts
    explicitly published addresses from "send your CV to", "apply at",
    "email us at", and high-signal HR local-part patterns.

    Args:
        description: Raw or cleaned job description text.

    Returns:
        Deduplicated list of valid, non-free-webmail email strings.
    """
    if not description:
        return []

    found: List[str] = []
    seen: set = set()

    for pattern in _DESCRIPTION_EMAIL_PATTERNS:
        for match in pattern.finditer(description):
            candidate = match.group(1).strip().lower()
            if not _EMAIL_VALIDATE_RE.match(candidate):
                continue
            domain = candidate.split("@", 1)[1]
            if domain in _FREE_WEBMAIL:
                continue
            if candidate not in seen:
                seen.add(candidate)
                found.append(candidate)

    return found


_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "config", "skills_list.yaml"
)

# Job type keyword mapping → canonical value
_JOB_TYPE_MAP = {
    "full time": "fulltime",
    "full-time": "fulltime",
    "fulltime": "fulltime",
    "part time": "parttime",
    "part-time": "parttime",
    "contract": "contract",
    "freelance": "freelance",
    "internship": "internship",
    "intern": "internship",
    "trainee": "internship",
    "temporary": "contract",
}

# Remote type keyword → canonical value
_REMOTE_MAP = {
    "remote": "remote",
    "work from home": "remote",
    "wfh": "remote",
    "hybrid": "hybrid",
    "onsite": "onsite",
    "on-site": "onsite",
    "in office": "onsite",
    "in-office": "onsite",
}

# Experience pattern: "2-5 years", "3+ years", "minimum 2 years", "fresher"
_EXPERIENCE_RE = re.compile(
    r"(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)"
    r"|(\d+)\+\s*(?:years?|yrs?)"
    r"|(\d+)\s*(?:years?|yrs?)",
    re.IGNORECASE,
)


def _load_skills() -> List[str]:
    """Load the curated skill keyword list from skills_list.yaml.

    Returns:
        Flat list of lowercase skill keyword strings.
    """
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        skills: List[str] = []
        if isinstance(data, dict):
            for category_skills in data.values():
                if isinstance(category_skills, list):
                    skills.extend(str(s).lower() for s in category_skills)
        return skills
    except Exception as exc:
        logger.debug("Could not load skills_list.yaml", extra={"error": str(exc)})
        return []


# Load once at module level
_SKILLS_LIST: List[str] = _load_skills()


class JobCleanerPipeline:
    """Applies cleaning and enrichment to a raw job dict from any extractor.

    Performs:
    - Title and description text cleaning
    - Location normalisation
    - Salary parsing (from description if not already set)
    - Skill extraction from description
    - Experience range parsing
    - Job type classification
    - Remote type detection
    """

    def clean(self, raw: dict) -> dict:
        """Clean a raw job dict and return an enriched version.

        Args:
            raw: Raw job field dict from an extractor.

        Returns:
            Cleaned job dict with normalised fields, or None if title fails
            garbage validation.
        """
        cleaned = dict(raw)

        # Text cleaning
        title = TextCleaner.clean_field(raw.get("job_title", ""))
        cleaned["job_title"] = title

        # Task 1: Reject garbage titles (navigation labels, ALL_CAPS, too short)
        if _is_garbage_title(title):
            logger.debug(
                "Job title rejected as garbage",
                extra={"title": title, "job_url": raw.get("job_url", "")},
            )
            return None

        description = TextCleaner.clean_field(raw.get("description", ""))

        # Task 2: Extract apply emails from description BEFORE stripping
        raw_description_for_email = raw.get("description", "")
        if not raw.get("apply_email"):
            emails = extract_emails_from_description(raw_description_for_email)
            if emails:
                cleaned["apply_email"] = emails[0]
                logger.debug(
                    "Email extracted from description",
                    extra={"email": emails[0], "title": title},
                )

        cleaned["description"] = description

        # Location
        location_raw = raw.get("location", "")
        cleaned["location"] = _clean_location(location_raw)

        # Remote type — from explicit field or inferred from title/description
        if not raw.get("remote_type"):
            cleaned["remote_type"] = _detect_remote_type(
                cleaned["job_title"], description, cleaned["location"]
            )

        # Salary — parse from description if not already provided
        if not raw.get("salary_min") and not raw.get("salary_max"):
            sal_min, sal_max, _ = SalaryCleaner.clean_salary(
                _extract_salary_string(description)
            )
            cleaned["salary_min"] = sal_min
            cleaned["salary_max"] = sal_max

        # Skills
        cleaned["skills_required"] = extract_skills(description)

        # Experience
        exp_min, exp_max = parse_experience(description)
        if not raw.get("experience_min"):
            cleaned["experience_min"] = exp_min
        if not raw.get("experience_max"):
            cleaned["experience_max"] = exp_max

        # Job type
        if not raw.get("job_type"):
            cleaned["job_type"] = classify_job_type(
                cleaned["job_title"], description
            )

        # Remove internal routing flags
        cleaned.pop("_needs_detail_fetch", None)

        return cleaned


def extract_skills(text: str) -> List[str]:
    """Extract skill keywords from job description text.

    Uses the curated skills_list.yaml for matching.

    Args:
        text: Job description text.

    Returns:
        Deduplicated list of matched skill strings.
    """
    if not text or not _SKILLS_LIST:
        return []

    text_lower = text.lower()
    found: List[str] = []
    seen: set = set()

    for skill in _SKILLS_LIST:
        skill_lower = skill.lower()
        # Match as whole word/phrase using word boundary-aware check
        pattern = r"(?<![a-zA-Z0-9._])" + re.escape(skill_lower) + r"(?![a-zA-Z0-9._])"
        if re.search(pattern, text_lower) and skill_lower not in seen:
            seen.add(skill_lower)
            found.append(skill)

    return found


def parse_experience(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract experience range from a job description string.

    Handles patterns like:
    - "2-5 years" → (2, 5)
    - "3+ years" → (3, None)
    - "minimum 2 years" → (2, None)
    - "fresher" → (0, 0)

    Args:
        text: Job description or experience requirement text.

    Returns:
        Tuple of (min_years, max_years), either may be None.
    """
    if not text:
        return None, None

    text_lower = text.lower()

    if "fresher" in text_lower or "0 year" in text_lower or "no experience" in text_lower:
        return 0, 0

    match = _EXPERIENCE_RE.search(text_lower)
    if not match:
        return None, None

    g1, g2, g3, g4 = match.groups()
    if g1 and g2:
        return int(g1), int(g2)
    if g3:
        return int(g3), None
    if g4:
        return None, int(g4)

    return None, None


def classify_job_type(title: str, description: str) -> Optional[str]:
    """Classify job type from title and description keywords.

    Args:
        title: Cleaned job title.
        description: Cleaned job description.

    Returns:
        Canonical job_type string or None if not determinable.
    """
    combined = (title + " " + description).lower()
    for keyword, job_type in _JOB_TYPE_MAP.items():
        if keyword in combined:
            return job_type
    return None


def _detect_remote_type(
    title: str, description: str, location: str
) -> Optional[str]:
    """Detect remote type from title, description, and location.

    Args:
        title: Cleaned job title.
        description: Cleaned job description.
        location: Normalised location string.

    Returns:
        Canonical remote_type string or None.
    """
    combined = (title + " " + description + " " + location).lower()
    for keyword, remote_type in _REMOTE_MAP.items():
        if keyword in combined:
            return remote_type
    return None


def _clean_location(location: str) -> str:
    """Normalise a location string.

    Args:
        location: Raw location string.

    Returns:
        Cleaned location string.
    """
    if not location:
        return ""
    try:
        city, state = LocationCleaner.clean_location(location)
        if city and state:
            return f"{city}, {state}"
        return city or state or location.strip()
    except Exception:
        return location.strip()


def _extract_salary_string(text: str) -> Optional[str]:
    """Extract a salary-related substring from description text.

    Looks for common salary patterns to pass to SalaryCleaner.

    Args:
        text: Job description text.

    Returns:
        Salary substring or None.
    """
    pattern = re.compile(
        r"(?:salary|ctc|package|compensation|pay)[\s:]*"
        r"[₹$£€]?\s*[\d,.]+\s*(?:to|-)?\s*[\d,.]*\s*"
        r"(?:lpa|lakh|lac|k|thousand|per\s+month|pm)?",
        re.IGNORECASE,
    )
    match = pattern.search(text or "")
    return match.group(0) if match else None
