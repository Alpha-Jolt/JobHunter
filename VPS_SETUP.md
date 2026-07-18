# JobHunter VPS Setup

**Host path:** `/docker/JobHunter`  
**Branch:** `Feature/Deploy`  
**Public URLs**

| Host | Upstream | Purpose |
|------|----------|---------|
| `https://app.myjobhunter.in` | `127.0.0.1:3003` | Main webapp |
| `https://api.myjobhunter.in` | `127.0.0.1:8004` | Orchestration API (direct / webhooks) |
| `https://admin.myjobhunter.in` | `127.0.0.1:5004` | Admin UI |
| `https://admin-api.myjobhunter.in` | `127.0.0.1:8005` | Admin API |
| `https://myjobhunter.in` | `127.0.0.1:3002` | Marketing site (JobHunter-Website) |

> **Auth note:** the webapp calls **`/api/*` on the same origin** (`app.myjobhunter.in`).  
> Next.js rewrites those to `INTERNAL_API_URL` (`http://jobhunter-api:8000`).  
> That avoids browser CORS. `api.myjobhunter.in` is still required for health checks, docs, webhooks, and mobile.

---

## 1. One-time clone + nginx

```bash
cd /docker
git clone -b Feature/Deploy https://github.com/Alpha-Jolt/JobHunter.git JobHunter
cd /docker/JobHunter

# Nginx site (TLS via Cloudflare origin cert)
sudo cp deploy/nginx-app.myjobhunter.in.conf /etc/nginx/sites-available/app.myjobhunter.in
sudo ln -sf /etc/nginx/sites-available/app.myjobhunter.in /etc/nginx/sites-enabled/app.myjobhunter.in
sudo nginx -t && sudo systemctl reload nginx
```

Confirm cert files exist:

```bash
ls -l /etc/ssl/cloudflare/jobhunter/origin.pem /etc/ssl/cloudflare/jobhunter/origin.key
```

Cloudflare DNS (proxied): `app`, `api`, `admin`, `admin-api` → VPS IP.  
SSL mode: **Full (strict)** if origin cert covers `*.myjobhunter.in`.

---

## 2. Root `.env` (single file)

```bash
cd /docker/JobHunter
cp env.example .env
nano .env   # fill secrets — CI never overwrites this file
```

### Required production values (must match this shape)

```env
# ── Public / compose build args ───────────────────────────────────────────────
# same-origin = browser uses https://app.myjobhunter.in/api/* (no CORS)
NEXT_PUBLIC_API_BASE_URL=same-origin
NEXT_PUBLIC_APP_URL=https://app.myjobhunter.in
NEXT_PUBLIC_ADMIN_API_URL=https://admin-api.myjobhunter.in
NEXT_PUBLIC_MINIO_URL=https://app.myjobhunter.in
INTERNAL_API_URL=http://jobhunter-api:8000
ADMIN_API_INTERNAL_URL=http://admin-api:8003

# CORS for direct browser hits to api.myjobhunter.in (mobile / docs / legacy)
CORS_ORIGINS=https://app.myjobhunter.in,http://localhost:3000,http://localhost:5173

POSTGRES_USER=jobhunter
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=jobhunter

# ── Admin API ─────────────────────────────────────────────────────────────────
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=<openssl rand -hex 32>
ADMIN_EMAIL=sysadmin@myjobhunter.in
ADMIN_PASSWORD_HASH=<argon2id hash>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
POSTGRES_URL=postgresql+asyncpg://jobhunter:<POSTGRES_PASSWORD>@postgres:5432/jobhunter
REDIS_URL=redis://redis:6379/0
FRONTEND_URL=https://admin.myjobhunter.in
SCRAPER_LOG_PATH=../scraper/logs/scraper.log

# ── AI engine ─────────────────────────────────────────────────────────────────
APP_NAME=JobHunter-AIEngine
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
OPENROUTER_API_KEY=<key>
OPENROUTER_MODEL=openai/gpt-4o-mini
LLM_PRIMARY_PROVIDER=openrouter
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=60
MAX_VARIANTS_TOTAL=50
MAX_VARIANTS_PER_SESSION=15
PATH_SCRAPER_OUTPUT_DIR=output/final
PATH_AI_OUTPUT_DIR=ai_output
APPROVAL_KEYS={"k1": "<64-hex>"}
APPROVAL_ACTIVE_KEY=k1

# ── Observability ─────────────────────────────────────────────────────────────
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=<strong-password>

# ── Orchestration API ─────────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://jobhunter:<POSTGRES_PASSWORD>@postgres:5432/jobhunter
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY_APPROVAL=<openssl rand -hex 32>
APPROVAL_TOKEN_SECRET=<openssl rand -hex 32>
JWT_SECRET=<openssl rand -hex 32 — min 32 chars>
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=30
MIN_PASSWORD_LENGTH=8
COOKIE_SECURE=true
COOKIE_DOMAIN=.myjobhunter.in
MAX_APPLICATIONS_PER_DAY=10
MAIL_BRIDGE_URL=http://mail-bridge:3000
MAIL_BRIDGE_API_KEY=<key>
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=<same as MINIO_ROOT_USER>
MINIO_SECRET_KEY=<same as MINIO_ROOT_PASSWORD>
MINIO_BUCKET_NAME=jobhunter-resumes
MINIO_AVATAR_BUCKET_NAME=jobhunter-avatars
MINIO_SECURE=false
MINIO_ROOT_USER=<admin>
MINIO_ROOT_PASSWORD=<strong-password>
MINIO_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ALEMBIC_MIGRATIONS=true
INTERNAL_API_KEY=<openssl rand -hex 32>

# ── Scraper ───────────────────────────────────────────────────────────────────
HEADLESS=true
DEV_MODE=false
USE_DATABASE=true
PAGES_PER_SEARCH=5
```

Generate secrets:

```bash
openssl rand -hex 32    # JWT_SECRET, SECRET_KEY, etc.
openssl rand -hex 64    # APPROVAL_KEYS value / INTERNAL_API_KEY
openssl rand -base64 24 # passwords
```

---

## 3. Deploy / rebuild

```bash
cd /docker/JobHunter
git fetch origin Feature/Deploy
git checkout Feature/Deploy
git pull origin Feature/Deploy

docker compose -p jobhunter \
  -f DOCKER-COMPOSE.yml \
  -f DOCKER-COMPOSE.prod.yml \
  --env-file .env \
  up -d --build --remove-orphans

# migrations
sleep 15
docker compose -p jobhunter -f DOCKER-COMPOSE.yml -f DOCKER-COMPOSE.prod.yml \
  --env-file .env exec -T jobhunter-api alembic upgrade head
```

After changing **any** `NEXT_PUBLIC_*` or `INTERNAL_API_URL` / `ADMIN_API_INTERNAL_URL`, you **must rebuild** webapp/admin (those values are baked at image build time):

```bash
docker compose -p jobhunter -f DOCKER-COMPOSE.yml -f DOCKER-COMPOSE.prod.yml --env-file .env \
  up -d --build --force-recreate webapp admin jobhunter-api admin-api
```

---

## 4. Health checks (run on VPS)

```bash
# Containers + ports
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep jobhunter

# Local upstreams (must succeed)
curl -sS -m 5 http://127.0.0.1:3003/login -o /dev/null -w 'webapp:%{http_code}\n'
curl -sS -m 5 http://127.0.0.1:8004/health
echo
curl -sS -m 5 http://127.0.0.1:5004/login -o /dev/null -w 'admin:%{http_code}\n'
curl -sS -m 5 http://127.0.0.1:8005/health
echo

# Via nginx Host headers (HTTPS)
curl -sk --resolve api.myjobhunter.in:443:127.0.0.1 https://api.myjobhunter.in/health
echo
curl -sk --resolve app.myjobhunter.in:443:127.0.0.1 -o /dev/null -w 'app:%{http_code}\n' \
  https://app.myjobhunter.in/login
```

Public expected:

```bash
curl -sS https://api.myjobhunter.in/health
# {"status":"ok",...}

curl -sS -o /dev/null -w '%{http_code}\n' https://app.myjobhunter.in/login
# 200
```

---

## 5. Troubleshooting current browser errors

### A) `Status code: 502` + `Origin … not allowed by Access-Control-Allow-Origin`

**Root cause:** Cloudflare/nginx got **502 Bad Gateway** from origin (API container down / not listening on `8004`).  
A 502 body has **no CORS headers**, so Safari/Chrome also report a CORS error. Fix the 502 first.

```bash
# Is API up?
docker ps -a --filter name=jobhunter-api
docker logs --tail 100 jobhunter-api

# Is 8004 listening?
ss -lntp | grep 8004 || netstat -lntp | grep 8004
curl -v -m 3 http://127.0.0.1:8004/health

# Restart API (+ deps)
cd /docker/JobHunter
docker compose -p jobhunter -f DOCKER-COMPOSE.yml -f DOCKER-COMPOSE.prod.yml --env-file .env \
  up -d --force-recreate jobhunter-api postgres redis
```

Common causes:

| Symptom | Fix |
|---------|-----|
| `jobhunter-api` Exited / Restarting | `docker logs jobhunter-api` — often bad `DATABASE_URL` / `JWT_SECRET` too short / missing env |
| Port 8004 free but curl fails | Container not publishing `127.0.0.1:8004` — ensure `DOCKER-COMPOSE.prod.yml` is used |
| Nginx 502, curl localhost OK | Wrong nginx `proxy_pass` port, or SSL site not enabled |
| After rebuild, still old behaviour | Hard-refresh browser; confirm image rebuilt (`docker images \| grep jobhunter`) |

### B) Login works then dumps back to `/login`

Ensure `.env` has:

```env
COOKIE_SECURE=true
COOKIE_DOMAIN=.myjobhunter.in
NEXT_PUBLIC_API_BASE_URL=same-origin
```

Rebuild **webapp + jobhunter-api**, then clear site cookies for `myjobhunter.in` and retry.

### C) CSP: `Refused to load … static.cloudflareinsights.com`

Fixed in `webapp/next.config.ts` / `admin/next.config.ts` (`script-src` + `connect-src` allow Cloudflare Insights). Rebuild webapp/admin after pull.

Alternatively disable **Cloudflare Web Analytics** for the zone if you do not need the beacon.

### D) Confirm `.env` keys the app actually needs

```bash
cd /docker/JobHunter
grep -E '^(NEXT_PUBLIC_|INTERNAL_|ADMIN_API_|CORS_|COOKIE_|FRONTEND_URL|DATABASE_URL|JWT_SECRET|REDIS_URL)=' .env
```

Must include at least:

- `NEXT_PUBLIC_API_BASE_URL=same-origin`
- `INTERNAL_API_URL=http://jobhunter-api:8000`
- `CORS_ORIGINS=https://app.myjobhunter.in,...`
- `COOKIE_DOMAIN=.myjobhunter.in`
- `COOKIE_SECURE=true`
- `FRONTEND_URL=https://admin.myjobhunter.in`
- `JWT_SECRET` (≥ 32 chars)
- `DATABASE_URL` / `POSTGRES_URL` matching `POSTGRES_PASSWORD`

---

## 6. App login (no default user)

There is **no seeded user** for `app.myjobhunter.in`.

1. Open https://app.myjobhunter.in/signup  
2. Create account (password ≥ 8 chars)  
3. Sign in at https://app.myjobhunter.in/login  

**Admin** (`https://admin.myjobhunter.in`) uses `ADMIN_EMAIL` / password from your argon2 hash in `.env` (see comment next to `ADMIN_PASSWORD_HASH` in `env.example`).

---

## 7. Checklist

- [ ] Cloudflare DNS for `app` / `api` / `admin` / `admin-api`
- [ ] Nginx site `app.myjobhunter.in` enabled + `nginx -t` OK
- [ ] `/docker/JobHunter/.env` present (single root file)
- [ ] `NEXT_PUBLIC_API_BASE_URL=same-origin`
- [ ] `COOKIE_DOMAIN=.myjobhunter.in` + `COOKIE_SECURE=true`
- [ ] `CORS_ORIGINS` includes `https://app.myjobhunter.in`
- [ ] `curl http://127.0.0.1:8004/health` → `ok`
- [ ] `curl https://api.myjobhunter.in/health` → `ok` (not 502)
- [ ] Webapp/admin rebuilt after env/CSP changes
- [ ] Alembic migrations applied
- [ ] Signup + login works on app (cookies cleared once)
