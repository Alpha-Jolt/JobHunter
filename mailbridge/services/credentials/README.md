# @mail-bridge/credentials

## Overview

Credential management microservice for Mail-Bridge. Stores and manages email provider credentials (Gmail OAuth 2.0 tokens and SMTP configs) with AES-256-GCM encryption. The `encrypted_value` field is never returned in any API response.

## Key Capabilities

- **Gmail OAuth 2.0** — full OAuth flow; stores access + refresh tokens encrypted; auto-refresh on expiry
- **Outlook OAuth 2.0** — Microsoft identity platform flow; stores access + refresh tokens encrypted; auto-refresh on expiry
- **SMTP credentials** — stores host/port/user/pass encrypted; connection tested on save
- **AES-256-GCM encryption** — per-credential key derived via HKDF from `CREDENTIAL_MASTER_KEY` + `keyId`
- **Key rotation support** — `encryption_key_id` stored per credential for future re-encryption
- **Workspace isolation** — all operations scoped to the authenticated user's workspace

## Quick Start

```bash
cd services/credentials
cp .env.example .env
npm run dev   # starts on :3002
```

## API Reference

| Method | Path | Role | API Key Scope | Description |
|---|---|---|---|---|
| GET | `/api/credentials/gmail/connect` | owner | `credentials` | Returns Google OAuth consent URL |
| GET | `/api/credentials/gmail/callback` | Public (OAuth redirect) | N/A | Exchanges code, stores tokens |
| GET | `/api/credentials/outlook/connect` | owner | `credentials` | Returns Microsoft OAuth consent URL |
| GET | `/api/credentials/outlook/callback` | Public (OAuth redirect) | N/A | Exchanges code, stores tokens |
| POST | `/api/credentials/smtp` | owner | `credentials` | Add SMTP credential |
| GET | `/api/credentials` | owner | `credentials` | List credentials (no encrypted_value) |
| DELETE | `/api/credentials/:id` | owner | `credentials` | Soft-delete credential |
| POST | `/api/credentials/:id/test` | owner | `credentials` | Verify credential is accessible |

### POST `/api/credentials/smtp`
```json
Request: {
  "from_email": "me@example.com",
  "host": "smtp.example.com",
  "port": 587,
  "secure": false,
  "user": "me@example.com",
  "pass": "app-password",
  "imap_host": "imap.example.com",
  "imap_port": 993,
  "imap_secure": true,
  "imap_sync_mode": "idle",
  "imap_poll_interval": 5
}
Response: { "success": true, "credential_id": "uuid", "from_email": "me@example.com", "provider_type": "smtp" }
```

### GET `/api/credentials`
```json
Response: {
  "success": true,
  "credentials": [
    { "credential_id": "uuid", "provider_type": "smtp", "from_email": "me@example.com", "is_active": true, "created_at": "..." }
  ]
}
```

**Error codes:** `INVALID_PAYLOAD` · `MISSING_CODE` · `OAUTH_FAILED` · `NOT_FOUND` · `MISSING_TOKEN` · `INVALID_TOKEN` · `INSUFFICIENT_ROLE`

## Encryption Details

- Algorithm: AES-256-GCM
- Key derivation: HKDF-SHA256(`CREDENTIAL_MASTER_KEY`, `keyId`, `"mail-bridge-credential"`, 32 bytes)
- Ciphertext format: `base64(IV[12] || AuthTag[16] || Ciphertext)`
- `keyId` = UUID generated per credential; stored in `credentials.encryption_key_id`

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3002` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis (for auth blocklist check) |
| `JWT_SECRET` | Yes | — | JWT verification |
| `CREDENTIAL_MASTER_KEY` | Yes | — | 64 hex chars |
| `FRONTEND_URL` | Yes | `http://localhost:3010` | Webapp URL for OAuth callbacks |
| `GMAIL_CLIENT_ID` | Gmail only | — | Google OAuth client ID |
| `GMAIL_CLIENT_SECRET` | Gmail only | — | Google OAuth client secret |
| `GMAIL_REDIRECT_URI` | Gmail only | `http://localhost:3002/api/credentials/gmail/callback` | OAuth callback |
| `OUTLOOK_CLIENT_ID` | Outlook only | — | Azure app client ID |
| `OUTLOOK_CLIENT_SECRET` | Outlook only | — | Azure app client secret |
| `OUTLOOK_REDIRECT_URI` | Outlook only | `http://localhost:3002/api/credentials/outlook/callback` | OAuth callback |
| `OUTLOOK_TENANT_ID` | Outlook only | `common` | `common` for personal + org accounts |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, auth middleware, DB pool
- `googleapis 140.0.0` — Gmail OAuth 2.0
- `@azure/msal-node 2.9.2` — Outlook OAuth 2.0
- `@microsoft/microsoft-graph-client 3.0.7` — Outlook profile fetch
- `axios 1.6.0` — HTTP client

## Testing

```bash
npm test -- tests/unit        # 4 unit tests (encrypt/decrypt)
npm test -- tests/integration # requires DB + Redis + TEST_TOKEN env var
npm run test:coverage
```
