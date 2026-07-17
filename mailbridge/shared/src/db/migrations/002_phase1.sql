-- Mail-Bridge Phase 1 Migration
-- Additive only: no DROP on existing columns, no breaking changes

-- 1. Extend credentials provider_type to include 'outlook'
ALTER TABLE credentials
  DROP CONSTRAINT credentials_provider_type_check,
  ADD CONSTRAINT credentials_provider_type_check
    CHECK (provider_type IN ('gmail', 'outlook', 'smtp'));

-- 2. Add validation_rules to email_templates
ALTER TABLE email_templates
  ADD COLUMN IF NOT EXISTS validation_rules JSONB NOT NULL DEFAULT '{}';

-- 3. Template version history
CREATE TABLE IF NOT EXISTS email_template_versions (
  version_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id      UUID NOT NULL REFERENCES email_templates(template_id) ON DELETE CASCADE,
  version          INTEGER NOT NULL,
  name             TEXT NOT NULL,
  subject          TEXT NOT NULL,
  html             TEXT NOT NULL,
  variables        JSONB NOT NULL DEFAULT '[]',
  validation_rules JSONB NOT NULL DEFAULT '{}',
  snapshotted_by   UUID REFERENCES users(user_id),
  snapshotted_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (template_id, version)
);

-- 4. Scheduled emails
CREATE TABLE IF NOT EXISTS scheduled_emails (
  scheduled_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  credential_id UUID NOT NULL REFERENCES credentials(credential_id) ON DELETE CASCADE,
  to_email      TEXT NOT NULL,
  subject       TEXT NOT NULL,
  html          TEXT NOT NULL,
  variables     JSONB NOT NULL DEFAULT '{}',
  template_id   UUID REFERENCES email_templates(template_id) ON DELETE SET NULL,
  scheduled_at  TIMESTAMPTZ NOT NULL,
  status        TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'queued', 'cancelled')),
  created_by    UUID REFERENCES users(user_id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_emails_pending
  ON scheduled_emails (scheduled_at)
  WHERE status = 'pending';

-- 5. Webhooks
CREATE TABLE IF NOT EXISTS webhooks (
  webhook_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  url           TEXT NOT NULL,
  events        JSONB NOT NULL DEFAULT '["email.sent","email.failed"]',
  secret_hash   TEXT NOT NULL,
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_by    UUID REFERENCES users(user_id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Webhook delivery log
CREATE TABLE IF NOT EXISTS webhook_deliveries (
  delivery_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_id    UUID NOT NULL REFERENCES webhooks(webhook_id) ON DELETE CASCADE,
  email_id      UUID REFERENCES email_logs(email_id) ON DELETE SET NULL,
  event         TEXT NOT NULL,
  payload       JSONB NOT NULL,
  status        TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'delivered', 'failed')),
  attempts      INTEGER NOT NULL DEFAULT 0,
  next_retry_at TIMESTAMPTZ,
  last_error    TEXT,
  delivered_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_retry
  ON webhook_deliveries (next_retry_at)
  WHERE status = 'pending';
