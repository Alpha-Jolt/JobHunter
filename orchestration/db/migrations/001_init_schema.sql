-- JobHunter Phase 0 — Initial Schema Migration
-- File: 001_init_schema.sql
-- Description: Creates all 6 core tables with constraints, indexes, and defaults.

-- ─────────────────────────────────────────────
-- 1. jobs
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    job_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          VARCHAR(50)  NOT NULL,
    external_id     VARCHAR(255) NOT NULL,
    title           VARCHAR(500) NOT NULL,
    company_name    VARCHAR(255) NOT NULL,
    company_domain  VARCHAR(255),
    location        VARCHAR(255),
    remote_type     VARCHAR(20)  CHECK (remote_type IN ('onsite', 'hybrid', 'remote')),
    salary_min      NUMERIC(12, 2),
    salary_max      NUMERIC(12, 2),
    experience_min  INTEGER,
    experience_max  INTEGER,
    description     TEXT         NOT NULL,
    skills_required TEXT[]       NOT NULL DEFAULT '{}',
    job_type        VARCHAR(20)  NOT NULL DEFAULT 'fulltime',
    apply_email     VARCHAR(255),
    email_trust     VARCHAR(20)  NOT NULL DEFAULT 'unknown'
                        CHECK (email_trust IN ('unknown', 'verified', 'low')),
    apply_url       TEXT,
    posted_at       TIMESTAMP WITH TIME ZONE,
    scraped_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status          VARCHAR(20)  NOT NULL DEFAULT 'raw'
                        CHECK (status IN ('raw', 'reviewed', 'applied', 'closed')),
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT jobs_source_external_id_unique UNIQUE (source, external_id),
    CONSTRAINT jobs_salary_range CHECK (
        salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max
    )
);

CREATE INDEX IF NOT EXISTS idx_jobs_status      ON jobs (status);
CREATE INDEX IF NOT EXISTS idx_jobs_source      ON jobs (source);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at  ON jobs (created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_apply_email ON jobs (apply_email) WHERE apply_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_last_seen   ON jobs (last_seen_at);

-- ─────────────────────────────────────────────
-- 2. master_resumes
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS master_resumes (
    resume_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         VARCHAR(255) NOT NULL,
    file_name       VARCHAR(500) NOT NULL,
    file_path       TEXT         NOT NULL,
    parsed_json     JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_master_resumes_user_id    ON master_resumes (user_id);
CREATE INDEX IF NOT EXISTS idx_master_resumes_created_at ON master_resumes (created_at);

-- ─────────────────────────────────────────────
-- 3. resume_variants
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resume_variants (
    variant_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           VARCHAR(255) NOT NULL,
    job_id            UUID         NOT NULL REFERENCES jobs (job_id) ON DELETE CASCADE,
    master_resume_id  UUID         NOT NULL REFERENCES master_resumes (resume_id) ON DELETE RESTRICT,
    pdf_key           TEXT         NOT NULL DEFAULT '',
    docx_key          TEXT         NOT NULL DEFAULT '',
    cover_letter_key  TEXT         NOT NULL DEFAULT '',
    local_pdf_path    TEXT         NOT NULL DEFAULT '',
    s3_upload_failed  BOOLEAN      NOT NULL DEFAULT FALSE,
    curated_json      JSONB        NOT NULL DEFAULT '{}',
    gaps_identified   TEXT[]       NOT NULL DEFAULT '{}',
    approval_status   VARCHAR(20)  NOT NULL DEFAULT 'pending'
                          CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    approval_token    VARCHAR(128),
    approved_at       TIMESTAMP WITH TIME ZONE,
    user_feedback     TEXT,
    prompt_version    VARCHAR(50)  NOT NULL DEFAULT '',
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT resume_variants_user_job_unique UNIQUE (user_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_variants_user_id         ON resume_variants (user_id);
CREATE INDEX IF NOT EXISTS idx_variants_job_id          ON resume_variants (job_id);
CREATE INDEX IF NOT EXISTS idx_variants_approval_status ON resume_variants (approval_status);
CREATE INDEX IF NOT EXISTS idx_variants_created_at      ON resume_variants (created_at);

-- ─────────────────────────────────────────────
-- 4. cover_letters
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cover_letters (
    cover_letter_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          VARCHAR(255) NOT NULL,
    job_id           UUID         NOT NULL REFERENCES jobs (job_id) ON DELETE CASCADE,
    variant_id       UUID         REFERENCES resume_variants (variant_id) ON DELETE SET NULL,
    content_text     TEXT         NOT NULL,
    file_key         TEXT         NOT NULL DEFAULT '',
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cover_letters_user_id    ON cover_letters (user_id);
CREATE INDEX IF NOT EXISTS idx_cover_letters_job_id     ON cover_letters (job_id);
CREATE INDEX IF NOT EXISTS idx_cover_letters_created_at ON cover_letters (created_at);

-- ─────────────────────────────────────────────
-- 5. application_log
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS application_log (
    application_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           VARCHAR(255) NOT NULL,
    job_id            UUID         NOT NULL REFERENCES jobs (job_id) ON DELETE RESTRICT,
    resume_variant_id UUID         NOT NULL REFERENCES resume_variants (variant_id) ON DELETE RESTRICT,
    cover_letter_id   UUID         REFERENCES cover_letters (cover_letter_id) ON DELETE SET NULL,
    status            VARCHAR(30)  NOT NULL DEFAULT 'sent'
                          CHECK (status IN ('sent', 'replied', 'interview_scheduled', 'rejected', 'ghosted')),
    sent_at           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at  TIMESTAMP WITH TIME ZONE,
    thread_id         VARCHAR(255),
    email_subject     VARCHAR(500),
    reply_count       INTEGER      NOT NULL DEFAULT 0 CHECK (reply_count >= 0),
    notes             TEXT,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT application_log_user_job_unique UNIQUE (user_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_application_log_user_id    ON application_log (user_id);
CREATE INDEX IF NOT EXISTS idx_application_log_job_id     ON application_log (job_id);
CREATE INDEX IF NOT EXISTS idx_application_log_sent_at    ON application_log (sent_at);
CREATE INDEX IF NOT EXISTS idx_application_log_status     ON application_log (status);
CREATE INDEX IF NOT EXISTS idx_application_log_created_at ON application_log (created_at);

-- ─────────────────────────────────────────────
-- 6. scraper_runs
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scraper_runs (
    run_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          VARCHAR(50)  NOT NULL,
    keywords        TEXT[]       NOT NULL DEFAULT '{}',
    locations       TEXT[]       NOT NULL DEFAULT '{}',
    pages_requested INTEGER      NOT NULL DEFAULT 1,
    status          VARCHAR(20)  NOT NULL DEFAULT 'queued'
                        CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    jobs_fetched    INTEGER      NOT NULL DEFAULT 0 CHECK (jobs_fetched >= 0),
    jobs_inserted   INTEGER      NOT NULL DEFAULT 0 CHECK (jobs_inserted >= 0),
    errors          INTEGER      NOT NULL DEFAULT 0 CHECK (errors >= 0),
    error_detail    TEXT,
    started_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scraper_runs_source       ON scraper_runs (source);
CREATE INDEX IF NOT EXISTS idx_scraper_runs_status       ON scraper_runs (status);
CREATE INDEX IF NOT EXISTS idx_scraper_runs_started_at   ON scraper_runs (started_at);
CREATE INDEX IF NOT EXISTS idx_scraper_runs_completed_at ON scraper_runs (completed_at);
