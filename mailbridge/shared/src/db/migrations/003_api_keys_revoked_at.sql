-- Mail-Bridge Phase 0 Migration 003
-- Adds revocation support and indexes to api_keys
-- Safe on fresh installs (auto via docker-entrypoint-initdb.d)
-- Existing installs: psql $DATABASE_URL -f shared/src/db/migrations/003_api_keys_revoked_at.sql

ALTER TABLE api_keys
  ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_api_keys_workspace ON api_keys(workspace_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash      ON api_keys(key_hash);
