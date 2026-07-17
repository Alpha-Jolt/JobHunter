"""Apify actor field mappings."""

ACTOR_FIELD_MAPS = {
    # Default / auto-detected fallback
    "default": {
        "title":        ["title", "jobTitle", "job_title", "name", "position"],
        "company_name": ["company", "companyName", "company_name", "employer"],
        "location":     ["location", "jobLocation", "place"],
        "description":  ["description", "jobDescription", "details", "content", "descriptionHtml"],
        "apply_url":    ["url", "jobUrl", "applyUrl", "link"],
        "salary_raw":   ["salary", "salaryRange", "compensation"],
        "posted_date":  ["postedAt", "posted_date", "datePosted", "date"],
        "job_type":     ["jobType", "employment_type", "type"],
    },
    # bebity/linkedin-jobs-scraper
    "bebity/linkedin-jobs-scraper": {
        "title":        ["title"],
        "company_name": ["companyName"],
        "location":     ["location"],
        "description":  ["descriptionHtml", "description"],
        "apply_url":    ["jobUrl"],
        "posted_date":  ["postedAt"],
    },
    # apify/indeed-scraper
    "apify/indeed-scraper": {
        "title":        ["positionName"],
        "company_name": ["company"],
        "location":     ["location"],
        "description":  ["description"],
        "apply_url":    ["url"],
        "salary_raw":   ["salary"],
        "posted_date":  ["postedAt"],
    },
    # apify/naukri-scraper (hypothetical/example if it exists)
    "apify/naukri-scraper": {
        "title":        ["title"],
        "company_name": ["companyName"],
        "location":     ["locations"],
        "description":  ["jobDescription"],
        "apply_url":    ["jobUrl"],
        "salary_raw":   ["salary"],
        "posted_date":  ["createdDate"],
    }
}
