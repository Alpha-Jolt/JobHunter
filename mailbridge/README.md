# Mail-Bridge

## Overview

Mail-Bridge is a production-grade, multi-tenant email delivery platform built as a microservices monorepo. It provides multi-provider email sending (Gmail OAuth 2.0, Outlook OAuth 2.0, SMTP), Handlebars templating with versioning, async delivery queues, webhook event delivery, and a full management console — all deployable via Docker Compose.

## Key Capabilities

- **Multi-provider email** — Gmail OAuth 2.0, Outlook OAuth 2.0, and any SMTP/IMAP server; credentials stored AES-256-GCM encrypted
- **Flexible payload** — no mandatory domain fields; users define their own email structure and template variables
- **Tier-based access control** — Free/Pro use flat owner+member roles; Enterprise uses full RBAC via `workspace_roles` (Free tier owners can upgrade to Pro directly from the console)
- **Async email queue** — Redis FIFO queue with automatic 3-retry worker loop per emails service instance
- **Inbound Emails** — fetch incoming emails metadata via Gmail Pub/Sub, Outlook Graph webhooks, and IMAP (Idle/Polling)
- **Handlebars templates** — versioned, rollback-capable, with variable validation
- **Webhooks** — HMAC-signed event delivery with exponential backoff retry for sent and received emails
- **API Keys** — headles REST API authentication with fine-grained scopes (`send`, `read`, etc.) and non-blocking `last_used_at` tracking
- **Management console** — Next.js 15 webapp with httpOnly cookie auth, full dashboard
- **Marketing site** — Next.js 15 static site with landing page, pricing, and MDX docs
- **API gateway** — Nginx reverse proxy with rate limiting and device fingerprinting
## License

Mail-Bridge is distributed under the **Business Source License (BUSL) 1.1**. 
- Source code is viewable for security auditing and debugging.
- Non-production/development use is free.
- Production use requires a commercial license key, or a free tier key.
- The code converts to an Open Source license (Apache 2.0) on June 28, 2029.

See `LICENSE` for details. Obtain a key at `https://mail-bridge.io/license`.

## Architecture

```
Browser
  ├── webapp:3010  (management console — Next.js 15)
  └── website:3011 (marketing site — Next.js 15, SSG)
         │
         ▼
  gateway:3009  (Nginx — rate limiting, routing)
         │
  ┌──────┴──────────────────────────────────────┐
  │  auth:3001   credentials:3002   emails:3003  │
  │  templates:3004   admin:3005   health:3006   │
  │  webhooks:3008                               │
  └──────────────────────────────────────────────┘
         │
  PostgreSQL:5432   Redis:6379
```

## Services

| Component | Port | Responsibility |
|---|---|---|
| `gateway` | 3009 | Nginx reverse proxy, rate limiting, routing |
| `webapp` | 3010 | Next.js management console |
| `website` | 3011 | Next.js marketing site + docs |
| `auth` | 3001 | Register, login, logout, token refresh |
| `credentials` | 3002 | Gmail + Outlook OAuth 2.0 + SMTP credential management |
| `emails` | 3003 | Send, batch, schedule emails; async worker; webhook event publisher |
| `templates` | 3004 | Template CRUD with versioning, rollback, variable validation |
| `admin` | 3005 | User and workspace management |
| `health` | 3006 | Liveness and readiness checks |
| `dashboard` | 3007 | Server-rendered status dashboard |
| `webhooks` | 3008 | Webhook CRUD + Redis pub/sub delivery + exponential backoff retry |

## Quick Start

**Prerequisites:** Docker + Docker Compose

```bash
# 1. Configure environment
cp .env.example .env
# Fill in: JWT_SECRET (min 32 chars), CREDENTIAL_MASTER_KEY (64 hex chars)

# 2. Start everything
docker-compose up -d

# 3. Open the console
open http://localhost:3010/register

# 4. Open the marketing site
open http://localhost:3011
```

**Development (without Docker):**

```bash
# Install all service dependencies
npm install

# Run database migration
psql $DATABASE_URL -f shared/src/db/migrations/001_initial.sql

# Start services individually
cd services/auth && npm run dev        # :3001
cd services/emails && npm run dev      # :3003
# ... etc

# Start frontend apps
cd webapp && npm install && npm run dev    # :3010
cd website && npm install && npm run dev  # :3011
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `JWT_SECRET` | Yes | Min 32 chars — signs all JWTs |
| `CREDENTIAL_MASTER_KEY` | Yes | 64 hex chars — AES-256-GCM master key |
| `FRONTEND_URL` | Yes | Frontend application URL for OAuth redirects |
| `GMAIL_CLIENT_ID` | Gmail only | Google OAuth client ID |
| `GMAIL_CLIENT_SECRET` | Gmail only | Google OAuth client secret |
| `GMAIL_REDIRECT_URI` | Gmail only | OAuth callback URL |
| `OUTLOOK_CLIENT_ID` | Outlook only | Azure AD app client ID |
| `OUTLOOK_CLIENT_SECRET` | Outlook only | Azure AD app client secret |
| `LOG_LEVEL` | No | `debug`/`info`/`warn`/`error` (default: `info`) |

**webapp only:**

| Variable | Required | Description |
|---|---|---|
| `API_GATEWAY_URL` | Yes | Internal gateway URL — server-side only, never `NEXT_PUBLIC_` |

## Dependencies

### Backend services (shared)
- `express 4.18.2`, `pino 8.17.0`, `pg 8.11.3`, `ioredis 5.3.2`
- `jsonwebtoken 9.0.2`, `argon2 0.31.2`, `handlebars 4.7.7`
- `googleapis 140.0.0`, `nodemailer 6.9.7`, `axios 1.6.0`

### webapp
- `next 15.1.0`, `react 19.0.0`, `@tanstack/react-query 5.62.0`, `zustand 4.4.7`
- `react-hook-form 7.76.1`, `zod 3.22.4`, `jwt-decode 4.0.0`

### website
- `next 15.1.0`, `react 19.0.0`, `next-mdx-remote 5.0.0`, `framer-motion 12.40.0`

## Testing

```bash
# Unit tests (no DB/Redis required)
cd services/auth && npm test -- tests/unit
cd services/emails && npm test -- tests/unit

# Integration tests (requires mailbridge_test DB + Redis DB 1)
cd services/auth && npm test -- tests/integration

# All unit tests across workspace
npm test --workspaces --if-present
```

## Integration Guide

All API traffic routes through the gateway at port 3009. Services communicate via shared PostgreSQL and Redis — no direct HTTP between services. The `emails` service publishes webhook events to Redis channel `webhook:events`; the `webhooks` service subscribes and handles delivery.

## Known Limitations

- Analytics dashboard not yet implemented (Phase 2)
- Subscription enforcement / rate limiting not yet implemented (Phase 2)
- No TLS termination at gateway in Phase 1 — add SSL for production
- Docs search (Fuse.js) not yet wired in website (Phase 2)

## Future Roadmap

- Phase 2: Analytics, subscription enforcement, A/B testing, audit logs, docs search
- Phase 3: White-label, SSO/SAML, additional providers, enterprise features
