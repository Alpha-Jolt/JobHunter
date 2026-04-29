"""Project-wide constants."""

# Scraper domains
INDEED_DOMAIN = "in.indeed.com"
NAUKRI_DOMAIN = "www.naukri.com"
LINKEDIN_DOMAIN = "www.linkedin.com"

# Timeouts (ms)
DEFAULT_PAGE_TIMEOUT_MS = 30_000
DEFAULT_NAVIGATION_TIMEOUT_MS = 30_000

# Retry
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 2.0
DEFAULT_MAX_DELAY = 60.0

# Scoring
COMPLETENESS_REQUIRED_FIELDS = [
    "title",
    "company_name",
    "description",
    "location_city",
    "salary_min_inr",
    "experience_min_years",
    "job_type",
    "apply_url",
]

# Output
OUTPUT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
