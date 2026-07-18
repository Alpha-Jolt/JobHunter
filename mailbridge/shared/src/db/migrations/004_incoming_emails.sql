-- Mail-Bridge Phase 0: Incoming Emails Schema

-- 1. Extend credentials table with IMAP configurations
ALTER TABLE credentials
  ADD COLUMN IF NOT EXISTS imap_host TEXT,
  ADD COLUMN IF NOT EXISTS imap_port INTEGER,
  ADD COLUMN IF NOT EXISTS imap_secure BOOLEAN,
  ADD COLUMN IF NOT EXISTS imap_sync_mode TEXT CHECK (imap_sync_mode IN ('idle', 'polling')),
  ADD COLUMN IF NOT EXISTS imap_poll_interval INTEGER;

-- 2. Create incoming email logs table
CREATE TABLE IF NOT EXISTS incoming_email_logs (
  log_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  credential_id UUID NOT NULL REFERENCES credentials(credential_id) ON DELETE CASCADE,
  from_address  TEXT NOT NULL,
  subject       TEXT,
  received_at   TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for querying incoming logs efficiently
CREATE INDEX IF NOT EXISTS idx_incoming_email_logs_workspace ON incoming_email_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_incoming_email_logs_created ON incoming_email_logs(created_at DESC);
