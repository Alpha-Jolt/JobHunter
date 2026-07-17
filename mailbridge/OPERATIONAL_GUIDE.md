# Mail-Bridge — Operational Guide

## Purpose & Scope

Mail-Bridge is a multi-tenant email delivery platform. This guide covers setup, operation, monitoring, troubleshooting, and maintenance for all 7 microservices and their shared infrastructure (PostgreSQL, Redis).

---

## Prerequisites

### System Requirements
- Node.js 18+, npm 11+
- PostgreSQL 15+
- Redis 7+ (self-hosted, `appendonly yes`)
- Docker + Docker Compose (for containerized deployment)

### Access Requirements
- PostgreSQL superuser (for initial migration)
- Redis access (no auth required in default config; add `requirepass` for production)
- Google Cloud Console project (for Gmail OAuth only)

---

## Installation & Setup

### Step 1: Install dependencies
```bash
cd Version2
npm install
```

### Step 2: Configure environment
```bash
cp .env.example .env
```

Minimum required values:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/mailbridge
REDIS_URL=redis://localhost:6379
JWT_SECRET=<min-32-char-random-string>
CREDENTIAL_MASTER_KEY=<64-hex-chars>
FRONTEND_URL=http://localhost:3010
API_GATEWAY_URL=https://your-public-domain.com
```

Generate a secure master key:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Step 3: Run database migration
```bash
psql $DATABASE_URL -f shared/src/db/migrations/001_initial.sql
```

### Step 4: Start services

**Development (individual):**
```bash
cd services/auth && npm run dev        # :3001
cd services/credentials && npm run dev # :3002
cd services/emails && npm run dev      # :3003
cd services/templates && npm run dev   # :3004
cd services/admin && npm run dev       # :3005
cd services/health && npm run dev      # :3006
cd services/dashboard && npm run dev   # :3007
cd services/webhooks && npm run dev    # :3008
```

**Production (Docker Compose):**
```bash
docker-compose up -d
docker-compose logs -f
```

### Step 5: Verify
```bash
curl http://localhost:3006/health
# → { "status": "ok", "version": "2.0.0" }

curl http://localhost:3006/health/ready
# → { "status": "ready", "db": "ok", "redis": "ok" }
```

---

## Operation Procedures

### Starting all services
```bash
docker-compose up -d
```

### Stopping all services
```bash
docker-compose down
```
Data is preserved in `postgres_data` and `redis_data` Docker volumes.

### Restarting a single service
```bash
docker-compose restart emails
```

### Viewing logs
```bash
docker-compose logs -f auth          # auth service only
docker-compose logs -f               # all services
```

---

## Service Port Reference

| Service | Port | Health endpoint |
|---|---|---|
| gateway | 3009 | `GET /health` |
| webapp | 3010 | `GET /` |
| website | 3011 | `GET /` |
| auth | 3001 | — |
| credentials | 3002 | — |
| emails | 3003 | — |
| templates | 3004 | — |
| admin | 3005 | — |
| health | 3006 | `GET /health`, `GET /health/ready` |
| dashboard | 3007 | `GET /` (requires JWT) |
| webhooks | 3008 | — |

---

## Monitoring

### Health Checks
```bash
# Liveness
curl http://localhost:3006/health

# Readiness (DB + Redis)
curl http://localhost:3006/health/ready
```

Expected healthy response:
```json
{ "status": "ready", "db": "ok", "redis": "ok" }
```

### Key Metrics to Watch
- `email_logs.status = 'failed'` count — indicates provider or credential issues
- `email_logs.retry_count >= 3` — emails that exhausted retries
- Redis queue depth: `redis-cli LLEN mail:queue` — should stay near 0 under normal load
- PostgreSQL connection count: `SELECT count(*) FROM pg_stat_activity`

### Log Locations
- All services log structured JSON to stdout
- Docker: `docker-compose logs -f <service>`
- Log level controlled by `LOG_LEVEL` env var (default: `info`)

### Log Fields
Every log entry includes `req_id` for request tracing. Key events:

| Level | Event |
|---|---|
| `info` | User registered, email queued, email sent |
| `warn` | Email job requeued (retry) |
| `error` | Email job failed, DB/Redis error |
| `fatal` | Uncaught exception or unhandled rejection — service exits |

---

## Troubleshooting

### Issue: Service fails to start — `Missing required env var`
**Diagnostic:** Check `.env` file has all required variables.
**Resolution:** Add missing variable. Required: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `CREDENTIAL_MASTER_KEY`.

### Issue: `GET /health/ready` returns 503
**Diagnostic:**
```bash
psql $DATABASE_URL -c "SELECT 1"   # test DB
redis-cli -u $REDIS_URL ping       # test Redis
```
**Resolution:** Start PostgreSQL or Redis if down. Check `DATABASE_URL` and `REDIS_URL` values.

### Issue: Emails stuck in `queued` status
**Diagnostic:** Check emails service logs for worker errors.
```bash
docker-compose logs emails | grep "Worker"
redis-cli LLEN mail:queue   # queue depth
```
**Resolution:** Restart emails service. If credential is invalid, delete and re-add it.

### Issue: Email status `failed` after 3 retries
**Diagnostic:** Check `email_logs.metadata` for error details.
```sql
SELECT email_id, metadata FROM email_logs WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;
```
**Resolution:** Verify credential is valid (`POST /api/credentials/:id/test`). Check provider (Gmail/SMTP) is reachable.

### Issue: `401 INVALID_TOKEN` on all requests after logout
**Cause:** Token was blocklisted in Redis on logout. Expected behavior.

### Issue: `403 INSUFFICIENT_SCOPE` when using an API Key
**Diagnostic:** Check the scopes assigned to the API Key in the Management Console.
**Resolution:** Ensure the API key has the necessary scope (e.g., `send` for sending emails, `read` for retrieving stats). Create a new key if needed, as scopes cannot be changed after creation.
**Resolution:** Log in again to get a new token.

### Issue: `409 EMAIL_EXISTS` on register
**Cause:** Email already registered.
**Resolution:** Use login endpoint instead, or use a different email.

### Issue: Service fails with `Cannot read file .../shared/tsconfig.base.json` locally
**Cause:** The `tsconfig.json` files extended `./shared/tsconfig.base.json`, which was only correct in the flattened Docker builder environment, breaking local compilation and editor tooling on the host.
**Resolution:** The configurations have been updated to extend `../../shared/tsconfig.base.json`. The Docker builder resolves this by creating a symlink `RUN ln -s /app/shared /shared` in the builder stage.

### Emergency: Complete service failure
1. `docker-compose down`
2. Check disk space: `df -h`
3. Check PostgreSQL: `docker-compose logs postgres`
4. Check Redis: `docker-compose logs redis`
5. `docker-compose up -d`
6. Verify: `curl http://localhost:3006/health/ready`

---

## Inbound Emails (Webhooks) Configuration

To receive incoming emails from OAuth providers (Gmail and Outlook), Mail-Bridge relies on Provider Webhooks. Since webhooks require a publicly accessible URL, you must configure `API_GATEWAY_URL` in your `.env` to point to a public domain (e.g., `https://mailbridge.example.com`).

### 1. Outlook Webhooks
No additional cloud setup is required. When a user connects their Outlook account, Mail-Bridge will automatically create a Graph API subscription using the `API_GATEWAY_URL`.

### 2. Gmail Push Notifications (Pub/Sub)
Gmail requires manual setup of Google Cloud Pub/Sub:
1. Go to Google Cloud Console.
2. Navigate to **Pub/Sub > Topics** and create a topic (e.g., `projects/YOUR_PROJECT_ID/topics/mailbridge-inbound`).
3. Grant Publish permissions to `gmail-api-push@system.gserviceaccount.com` on this topic.
4. Create a **Push Subscription** on the topic. Set the endpoint URL to: 
   `https://your-public-domain.com/api/inbound/gmail-push`
5. Update your `.env` file to configure the topic name (if needed for the backend).

For local development, use a tool like `ngrok` (e.g., `ngrok http 3009`) and set `API_GATEWAY_URL` to your ngrok forwarding URL.

---

## Testing

### Unit tests (no infrastructure required)
```bash
cd services/auth && npm test -- tests/unit --no-coverage
cd services/credentials && npm test -- tests/unit --no-coverage
cd services/emails && npm test -- tests/unit --no-coverage
```

### Integration tests (requires `mailbridge_test` DB + Redis DB 1)
```bash
# Create test DB
psql $DATABASE_URL -c "CREATE DATABASE mailbridge_test"
psql postgresql://user:pass@localhost:5432/mailbridge_test \
  -f shared/src/db/migrations/001_initial.sql

# Run
cd services/auth && npm test -- tests/integration
```

### Full coverage report
```bash
cd services/auth && npm run test:coverage
```

### API tests (Postman)
Import `services/emails/tests/api/mail-bridge.postman_collection.json` into Postman.
Use `dev.postman_environment.json` for local testing.

---

## Maintenance

### Daily
- Check `GET /health/ready` returns 200
- Monitor `email_logs` for `failed` status entries

### Weekly
- Review Redis queue depth: `redis-cli LLEN mail:queue`
- Check PostgreSQL table sizes: `SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC`

### Dependency updates
```bash
cd Version2
npm audit
# Review and update pinned versions in each service's package.json
```

---

## Security

### Credential Protection
- All email credentials (Gmail tokens, SMTP passwords) stored AES-256-GCM encrypted
- `CREDENTIAL_MASTER_KEY` must never be logged, committed, or exposed
- `encrypted_value` field is never returned in any API response

### JWT Security
- Tokens blocklisted in Redis on logout (TTL = remaining token lifetime)
- `JWT_SECRET` must be min 32 chars, randomly generated
- Token expiry: 24h default, configurable via `JWT_EXPIRES_IN`

### Access Control
- All routes except `/auth/register`, `/auth/login`, `/health` require valid JWT
- Role enforcement: `owner` required for credential and admin operations; `member` sufficient for sending emails and managing templates

### Rotating `CREDENTIAL_MASTER_KEY`
1. Generate new key: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
2. Re-encrypt all credentials with new key (migration script required — not automated in Phase 0)
3. Update `CREDENTIAL_MASTER_KEY` env var and restart services

---

## Data Management

### Database Schema
6 tables: `workspaces`, `users`, `workspace_roles`, `credentials`, `email_templates`, `email_logs`, `api_keys`

### Backup
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
psql $DATABASE_URL < backup_20260523.sql
```

### Data Retention
- `email_logs` grows unbounded in Phase 0 — add a cleanup job for logs older than 90 days in production
- `credentials` with `is_active = FALSE` can be purged after 30 days

---

## Scaling

### Horizontal scaling
Each service is stateless (state in PostgreSQL + Redis). Scale by running multiple instances behind a load balancer. Ensure all instances share the same `DATABASE_URL` and `REDIS_URL`.

### Email worker
The emails service runs one worker loop per instance. Multiple instances = multiple parallel workers consuming from the same Redis queue — safe by design (BRPOP is atomic).

---

## Disaster Recovery

### RTO: ~5 minutes (restart containers)
### RPO: Last PostgreSQL backup

### Recovery procedure
1. Restore PostgreSQL from backup
2. Redis data is ephemeral for queue (in-flight jobs may be lost — they will be re-sent manually)
3. `docker-compose up -d`
4. Verify health endpoint

---

## Contacts & Escalation

- Primary: Engineering team
- Escalation: Check `LOGS.md` for recent agent execution history

---

## Gateway (Nginx)

### Purpose
Single ingress point for all API traffic. Enforces rate limits and routes to upstream services.

### Port
`3009`

### Rate limits
- Auth routes (`/auth/*`): 5 req/min — brute-force protection
- API routes (`/api/*`): 100 req/s — general limit

### Start / stop
```bash
docker-compose up -d gateway
docker-compose stop gateway
```

### Verify
```bash
curl http://localhost:3009/health
# → { "status": "ok" }
```

### Troubleshooting

#### 502 Bad Gateway
Upstream service is down. Check:
```bash
docker-compose ps          # which services are running
docker-compose logs auth   # check specific service
```

#### 429 Too Many Requests
Rate limit hit. Wait for the limit window to reset (1 min for auth, 1s for API).

---

## webapp (Management Console)

### Purpose
Next.js 15 authenticated dashboard. All API calls proxied server-side through `API_GATEWAY_URL`.

### Port
`3010`

### Environment
```bash
cp webapp/.env.local.example webapp/.env.local
# Set API_GATEWAY_URL=http://gateway:3009  (Docker) or http://localhost:3009 (dev)
```

### Start
```bash
# Development
cd webapp && npm run dev

# Production (Docker)
docker-compose up -d webapp
```

### Verify
```bash
curl -I http://localhost:3010
# → HTTP/1.1 200 OK (redirects to /login if unauthenticated)
```

### Auth cookie
- Name: `mb_token`
- Type: httpOnly, sameSite=strict
- TTL: 86400s (24h)
- Set by: `POST /api/auth/login` (Next.js API route)

### Troubleshooting

#### Blank page / hydration error
Clear browser cookies and hard-refresh. If persistent, check `API_GATEWAY_URL` is set correctly.

#### 401 on all API calls after login
Cookie may have expired or been cleared. Log in again.

#### Owner-only pages redirect members
Expected behavior — middleware enforces RBAC based on JWT `role` claim.

---

## website (Marketing Site)

### Purpose
Next.js 15 static site. No backend connection — fully prerendered at build time.

### Port
`3011`

### Start
```bash
# Development
cd website && npm run dev

# Production (Docker)
docker-compose up -d website
```

### Adding a doc page
1. Create `website/content/docs/<slug>.mdx`
2. Add frontmatter: `title`, `description`, `lastUpdated`, `order`
3. Rebuild: `cd website && npm run build`

### Troubleshooting

#### Doc page returns 404
Check the file exists at `website/content/docs/<slug>.mdx` and the slug matches the URL exactly.

#### `gray-matter` Date serialization error
Ensure `lastUpdated` frontmatter value is quoted as a string: `lastUpdated: "2026-05-23"` or use `String()` coercion in `lib/docs.ts`.
