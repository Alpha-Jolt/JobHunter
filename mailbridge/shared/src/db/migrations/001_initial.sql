-- Mail-Bridge Phase 0 — Initial Schema
-- Run once against target database

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS workspaces (
  workspace_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  tier          TEXT NOT NULL DEFAULT 'free'
                  CHECK (tier IN ('free', 'pro', 'enterprise')),
  settings      JSONB NOT NULL DEFAULT '{}',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
  user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  workspace_id  UUID REFERENCES workspaces(workspace_id) ON DELETE SET NULL,
  role          TEXT NOT NULL DEFAULT 'member'
                  CHECK (role IN ('owner', 'member')),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at    TIMESTAMPTZ
);

-- Enterprise RBAC — only populated for enterprise tier workspaces
CREATE TABLE IF NOT EXISTS workspace_roles (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role          TEXT NOT NULL
                  CHECK (role IN ('system-admin', 'operational-admin', 'admin', 'user')),
  scope         JSONB NOT NULL DEFAULT '{}',
  assigned_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (workspace_id, user_id)
);

CREATE TABLE IF NOT EXISTS credentials (
  credential_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id      UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  provider_type     TEXT NOT NULL CHECK (provider_type IN ('gmail', 'smtp')),
  from_email        TEXT NOT NULL,
  encrypted_value   TEXT NOT NULL,
  encryption_key_id TEXT NOT NULL,
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  last_used_at      TIMESTAMPTZ,
  metadata          JSONB NOT NULL DEFAULT '{}',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_templates (
  template_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  subject       TEXT NOT NULL,
  html          TEXT NOT NULL,
  variables     JSONB NOT NULL DEFAULT '[]',
  created_by    UUID REFERENCES users(user_id) ON DELETE SET NULL,
  version       INTEGER NOT NULL DEFAULT 1,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_logs (
  email_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id        UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  credential_id       UUID REFERENCES credentials(credential_id) ON DELETE SET NULL,
  to_email            TEXT NOT NULL,
  from_email          TEXT NOT NULL,
  subject             TEXT NOT NULL,
  template_id         UUID REFERENCES email_templates(template_id) ON DELETE SET NULL,
  provider_message_id TEXT,
  status              TEXT NOT NULL DEFAULT 'queued'
                        CHECK (status IN ('queued', 'sent', 'failed', 'bounced')),
  sent_at             TIMESTAMPTZ,
  retry_count         INTEGER NOT NULL DEFAULT 0,
  metadata            JSONB NOT NULL DEFAULT '{}',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
  api_key_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  key_hash      TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  created_by    UUID REFERENCES users(user_id) ON DELETE SET NULL,
  last_used_at  TIMESTAMPTZ,
  expires_at    TIMESTAMPTZ,
  scopes        JSONB NOT NULL DEFAULT '["send"]',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_users_workspace ON users(workspace_id);
CREATE INDEX IF NOT EXISTS idx_credentials_workspace ON credentials(workspace_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_workspace ON email_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status);
CREATE INDEX IF NOT EXISTS idx_email_logs_created ON email_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workspace_roles_workspace ON workspace_roles(workspace_id);
