-- JobHunter Phase 0+ — Auth Schema Migration
-- File: 002_auth_schema.sql
-- Description: Creates users, refresh_tokens tables; alters user_id columns
--              in existing tables from VARCHAR to UUID with FK constraints;
--              adds nullable recruiter_id FK on jobs.

-- ─────────────────────────────────────────────
-- 1. users
-- ─────────────────────────────────────────────
CREATE TYPE user_role AS ENUM ('hunter', 'mentor', 'recruiter', 'admin');

CREATE TABLE IF NOT EXISTS users (
    user_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(255),
    last_name       VARCHAR(255),
    phone           VARCHAR(20),
    role            user_role NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at     TIMESTAMP WITH TIME ZONE,
    last_login_at   TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_users_email_format CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')
);

CREATE INDEX IF NOT EXISTS idx_users_email      ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role       ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_is_active  ON users (is_active);

-- ─────────────────────────────────────────────
-- 2. refresh_tokens
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS refresh_tokens (
    token_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,
    issued_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at  TIMESTAMP WITH TIME ZONE,

    CONSTRAINT refresh_tokens_user_hash_unique UNIQUE (user_id, token_hash)
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id    ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_revoked    ON refresh_tokens (revoked);

-- ─────────────────────────────────────────────
-- 3. Alter existing user_id columns VARCHAR → UUID + FK
--    Tables: master_resumes, resume_variants, cover_letters, application_log
--    DB is empty (Phase 0 dev) — safe to alter type directly.
-- ─────────────────────────────────────────────

-- master_resumes
ALTER TABLE master_resumes
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

ALTER TABLE master_resumes
    ADD CONSTRAINT fk_master_resumes_user_id
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;

-- resume_variants
ALTER TABLE resume_variants
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

ALTER TABLE resume_variants
    ADD CONSTRAINT fk_resume_variants_user_id
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;

-- cover_letters
ALTER TABLE cover_letters
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

ALTER TABLE cover_letters
    ADD CONSTRAINT fk_cover_letters_user_id
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;

-- application_log
ALTER TABLE application_log
    ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

ALTER TABLE application_log
    ADD CONSTRAINT fk_application_log_user_id
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;

-- ─────────────────────────────────────────────
-- 4. Add recruiter_id to jobs (nullable FK)
--    NULL = scraper-owned; UUID = recruiter-posted (Phase 1+)
-- ─────────────────────────────────────────────
ALTER TABLE jobs
    ADD COLUMN IF NOT EXISTS recruiter_id UUID
    REFERENCES users (user_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_jobs_recruiter_id ON jobs (recruiter_id) WHERE recruiter_id IS NOT NULL;
