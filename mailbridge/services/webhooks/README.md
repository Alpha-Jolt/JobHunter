# @mail-bridge/webhooks

## Overview

Webhook delivery microservice for Mail-Bridge. Subscribes to Redis `webhook:events` channel published by the `emails` service, delivers signed HTTP POST payloads to registered URLs, and retries failed deliveries with exponential backoff. Provides a management API for registering and monitoring webhooks.

## Key Capabilities

- **Event subscription** — listens on Redis pub/sub channel `webhook:events`; dispatches to all matching active workspace webhooks
- **HMAC-SHA256 signatures** — every delivery includes `X-Mail-Bridge-Signature: sha256=<hmac>` for receiver verification
- **Encrypted secrets** — webhook signing secrets stored AES-256-GCM encrypted; raw secret returned only at creation
- **Exponential backoff retry** — failed deliveries retried up to 5 times: 30s, 60s, 120s, 240s, 480s
- **Concurrency-safe retry loop** — `SELECT FOR UPDATE SKIP LOCKED` prevents duplicate retries across multiple instances
- **Delivery history** — paginated log of all delivery attempts per webhook
- **Test delivery** — `POST /api/webhooks/:id/test` sends a test payload immediately

## Quick Start

```bash
cd services/webhooks
cp .env.example .env
npm run dev   # starts on :3008
```

## Architecture

```
emails service worker
  → redis.publish('webhook:events', payload)
        ↓
webhooks service (Redis subscriber)
  → queries matching active webhooks for workspace
  → inserts webhook_deliveries record
  → POST to webhook URL with HMAC signature
  → on failure: exponential backoff retry loop (every 30s)
```

## API Reference

| Method | Path | Role | API Key Scope | Description |
|---|---|---|---|---|
| POST | `/api/webhooks` | owner | `admin` | Register a new webhook endpoint |
| GET | `/api/webhooks` | owner | `admin` | List all webhooks for workspace |
| PUT | `/api/webhooks/:id` | owner | `admin` | Update webhook (URL, events) |
| DELETE | `/api/webhooks/:id` | owner | `admin` | Delete webhook |
| GET | `/api/webhooks/:id/deliveries` | owner | `admin` | List delivery history (paginated) |
| POST | `/api/webhooks/:id/test` | owner | `admin` | Dispatch a test `email.sent` event |

### POST `/api/webhooks`
```json
Request:  { "url": "https://myapp.com/hook", "events": ["email.sent", "email.failed"], "secret": "my-raw-secret" }
Response: { "success": true, "webhook_id": "uuid", "secret": "my-raw-secret" }
```
> `secret` is shown **only in this response**. Store it — it cannot be retrieved again.

### Webhook payload shape
```json
{
  "event": "email.sent",
  "workspace_id": "uuid",
  "email_id": "uuid",
  "to_email": "recipient@example.com",
  "subject": "Hello",
  "sent_at": "2026-05-23T11:00:00.000Z",
  "provider_message_id": "..."
}
```

### Signature verification (receiver side)
```javascript
const crypto = require('crypto')
const expected = 'sha256=' + crypto.createHmac('sha256', YOUR_SECRET).update(rawBody).digest('hex')
if (req.headers['x-mail-bridge-signature'] !== expected) return res.status(401).end()
```

**Valid events:** `email.sent` | `email.failed` | `email.bounced`

**Error codes:** `INVALID_PAYLOAD` · `NOT_FOUND` · `MISSING_TOKEN` · `INVALID_TOKEN` · `INSUFFICIENT_ROLE`

## Retry Schedule

| Attempt | Delay |
|---|---|
| 1 | 30s |
| 2 | 60s |
| 3 | 120s |
| 4 | 240s |
| 5 (final) | 480s → marked `failed` |

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3008` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis (pub/sub + auth blocklist) |
| `JWT_SECRET` | Yes | — | JWT verification |
| `CREDENTIAL_MASTER_KEY` | Yes | — | 64 hex chars — used to encrypt webhook secrets |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, auth middleware, DB pool, shared crypto
- `axios 1.6.0` — HTTP delivery to webhook URLs

## Testing

```bash
npm test -- tests/unit        # 6 unit tests (dispatcher)
npm test -- tests/integration # requires DB + Redis + TEST_TOKEN
npm run test:coverage
```

### Unit tests cover
- Payload POST to webhook URL
- HMAC-SHA256 signature header
- Mark `delivered` on 2xx
- Increment attempts + set `next_retry_at` on failure
- Mark `failed` after 5 attempts
- `buildSignature` static method
