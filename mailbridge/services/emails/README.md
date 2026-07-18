# @mail-bridge/emails

## Overview

Email sending microservice for Mail-Bridge. Accepts send requests, renders Handlebars templates with user-defined variables, queues jobs to Redis, and processes them asynchronously via a built-in worker loop. Supports Gmail OAuth 2.0 and SMTP providers. Retries failed sends up to 3 times before marking as `failed`.

## Key Capabilities

- **Flexible payload** — no mandatory domain fields; any `subject`/`html` with any `variables`
- **Template support** — optionally reference a saved template by `template_id`; variables substituted at send time
- **Custom variable validation** — templates can define `required`, `maxLength`, `pattern` rules enforced at send time
- **Batch sending** — `POST /api/emails/batch` accepts up to `BATCH_MAX_SIZE` emails (default 100) in one request
- **Email scheduling** — `POST /api/emails/schedule` queues an email for a future UTC datetime; 1-minute cron resolution
- **Async queue** — jobs pushed to Redis FIFO queue; worker processes them in background
- **3-retry logic** — failed jobs requeued up to 3 times; then `status = 'failed'`
- **Multi-provider** — Gmail OAuth 2.0, Outlook OAuth 2.0 (Microsoft Graph), SMTP
- **Inbound Emails (New)** — listens for Gmail Pub/Sub and Outlook Graph webhooks, fetches email metadata, and stores in `incoming_email_logs`.
- **Attachment support** — attachments downloaded from URLs at send time, attached as buffers
- **Webhook events** — publishes `email.sent` / `email.failed` / `gmail.received` / `outlookmail.received` to Redis `webhook:events` channel
- **Paginated email logs** — full audit trail of all sends and receives per workspace

## Quick Start

```bash
cd services/emails
cp .env.example .env
npm run dev   # starts on :3003, worker starts automatically
```

## API Reference

| Method | Path | Role | API Key Scope | Description |
|---|---|---|---|---|
| POST | `/api/emails/send` | member | `send` | Queue a single email |
| POST | `/api/emails/batch` | member | `send` | Queue multiple emails (max `BATCH_MAX_SIZE`) |
| POST | `/api/emails/schedule` | member | `send` | Schedule email for a future UTC datetime |
| GET | `/api/emails/schedule` | member | `read` | List pending scheduled emails (paginated) |
| DELETE | `/api/emails/schedule/:id` | member | `send` | Cancel a scheduled email |
| GET | `/api/emails` | member | `read` | List email logs (paginated) |
| GET | `/api/emails/stats` | member | `read` | Get email status breakdown |
| GET | `/api/emails/:id` | member | `read` | Get single email log |

### POST `/api/emails/send`
```json
Request: {
  "credential_id": "uuid",
  "to_email": "recipient@example.com",
  "subject": "Hello {{name}}",
  "html": "<p>Hi {{name}}, welcome!</p>",
  "variables": { "name": "Alice" },
  "template_id": "uuid (optional — overrides subject/html)",
  "attachments": [
    { "filename": "report.pdf", "url": "https://storage.example.com/report.pdf" }
  ]
}
Response: { "success": true, "email_id": "uuid", "status": "queued" }
```

### GET `/api/emails?page=1&limit=20`
```json
Response: {
  "success": true,
  "emails": [ { "email_id": "...", "to_email": "...", "subject": "...", "status": "sent", "sent_at": "..." } ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

### GET `/api/emails/stats`
```json
Response: {
  "success": true,
  "stats": {
    "total": 105,
    "sent": 95,
    "failed": 8,
    "queued": 2,
    "today": 12
  }
}
```

### POST `/api/emails/batch`
```json
Request: { "emails": [ { "credential_id": "uuid", "to_email": "...", "subject": "...", "html": "...", "variables": {} } ] }
Response: { "success": true, "queued": 1, "email_ids": ["uuid"] }
```

### POST `/api/emails/schedule`
```json
Request: { "credential_id": "uuid", "to_email": "...", "subject": "...", "html": "...", "scheduled_at": "2026-06-01T09:00:00Z" }
Response: { "success": true, "scheduled_id": "uuid", "scheduled_at": "2026-06-01T09:00:00Z" }
```

**Email statuses:** `queued` → `sent` | `failed` | `bounced`

**Error codes:** `INVALID_PAYLOAD` · `NOT_FOUND` (credential or template) · `MISSING_TOKEN` · `INVALID_TOKEN`

## Worker Behavior

The worker starts automatically when the service starts. It:
1. Calls `BRPOP mail:queue 5` (blocks up to 5s waiting for a job)
2. Decrypts the credential from PostgreSQL
3. Downloads any attachments from their URLs
4. Calls the appropriate provider (`GmailProvider` or `SmtpProvider`)
5. Updates `email_logs` to `sent` with `provider_message_id`
6. On failure: increments `retry_count`; requeues if `< 3`; sets `failed` if `>= 3`

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3003` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis queue |
| `JWT_SECRET` | Yes | — | JWT verification |
| `CREDENTIAL_MASTER_KEY` | Yes | — | 64 hex chars for credential decryption |
| `GMAIL_CLIENT_ID` | Gmail only | — | Google OAuth client ID |
| `GMAIL_CLIENT_SECRET` | Gmail only | — | Google OAuth client secret |
| `OUTLOOK_CLIENT_ID` | Outlook only | — | Azure app client ID |
| `OUTLOOK_CLIENT_SECRET` | Outlook only | — | Azure app client secret |
| `OUTLOOK_TENANT_ID` | Outlook only | `common` | Azure tenant |
| `BATCH_MAX_SIZE` | No | `100` | Max emails per batch request |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, auth middleware, DB pool, Redis queue, shared crypto
- `handlebars 4.7.7` — template rendering
- `googleapis 140.0.0` — Gmail API send
- `@azure/msal-node 2.9.2` — Outlook token refresh
- `@microsoft/microsoft-graph-client 3.0.7` — Outlook send via Graph API
- `nodemailer 6.9.7` — SMTP send
- `node-cron 3.0.3` — scheduled email cron loop
- `axios 1.6.0` — attachment download

## Testing

```bash
npm test -- tests/unit        # 4 unit tests (composer)
npm test -- tests/integration # requires DB + Redis + TEST_TOKEN + TEST_CREDENTIAL_ID
npm test -- tests/e2e         # full flow test
npm run test:coverage
```

### API Tests
Import `tests/api/mail-bridge.postman_collection.json` into Postman.
Use `tests/api/dev.postman_environment.json` for local testing.
