# JobHunter Orchestration API

FastAPI service that orchestrates the scraper, job inventory, AI resume pipeline, mail sending, and admin monitoring for JobHunter.

> **Port:** 8000 | **Phase:** 1 | **Status:** Complete

---

## Quick Start

```bash
# Run from the project root (JobHunter/)
python3 -m venv orchestration/.venv
source orchestration/.venv/bin/activate
pip install -r orchestration/requirements.txt
cp orchestration/.env.example orchestration/.env
uvicorn orchestration.api.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
# Admin Dashboard: http://localhost:8000/admin
```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe — `{"status": "ok"}` |
| GET | `/readiness` | DB + job registry connectivity check |
| GET | `/` | Welcome message |
| POST | `/api/scraper/start` | Trigger a scraper run |
| GET | `/api/scraper/status/{run_id}` | Run status and aggregated counts |
| GET | `/api/scraper/latest-jobs` | Paginated active job list |
| GET | `/api/scraper/counts` | Job counts by source, status, email_trust |
| POST | `/api/ai/generate` | Generate resume variant for a job |
| GET | `/api/ai/pending/{user_id}` | List pending variants awaiting approval |
| GET | `/api/ai/preview/{variant_id}` | Preview curated resume before approving |
| POST | `/api/ai/approve/{variant_id}` | Approve variant via signed token |
| POST | `/api/ai/reject/{variant_id}` | Reject variant with optional feedback |
| POST | `/api/resume/upload` | Upload master resume (PDF/DOCX) to MinIO — hunter/admin only |
| POST | `/api/mail/send` | Send job application email via Mail-Bridge |
| GET | `/api/mail/status/{application_id}` | Get application send status |
| GET | `/api/mail/sent-today/{user_id}` | Applications sent by user in last 24h |
| GET | `/api/admin/dashboard/metrics` | Real-time system metrics |
| GET | `/api/admin/variants-pending` | All variants awaiting approval |
| GET | `/api/admin/applications-log` | Recent applications (paginated) |
| GET | `/api/admin/scraper-runs` | Recent scraper run history |

---

## Directory Structure

```
orchestration/
├── api/
│   ├── main.py          # FastAPI app, middleware, lifecycle
│   ├── config.py        # Pydantic Settings (5 config classes)
│   ├── middleware.py    # RequestID, Logging, ErrorHandling, CORS
│   ├── dependencies.py  # DI: get_db_session, get_mail_service, get_job_registry, etc.
│   └── routes/
│       ├── scraper.py   # /api/scraper/* endpoints
│       ├── ai.py        # /api/ai/* endpoints
│       ├── resume.py    # /api/resume/upload endpoint
│       ├── mail.py      # /api/mail/* endpoints
│       ├── admin.py     # /api/admin/* endpoints
│       └── health.py    # /health and /readiness endpoints
├── core/
│   ├── exceptions.py    # Domain exceptions (ApprovalRequiredError, MailSendError, etc.)
│   ├── logging_setup.py # Structured JSON logging with trace/span ID injection
│   ├── telemetry.py     # OTel bootstrap — Resource, Exporter, FastAPI/SQL/HTTPX/Redis instrumentors
│   ├── spans.py         # `traced()` async context manager for semantic business spans
│   └── metrics.py       # Business metric instruments (login_total, ai_request_duration, etc.)
├── db/
│   ├── connection.py    # Async engine, session factory
│   ├── models.py        # SQLAlchemy ORM (6 models)
│   └── migrations/
│       └── 001_init_schema.sql
├── repositories/
│   ├── postgres_job_repository.py
│   ├── postgres_variant_repository.py
│   ├── postgres_application_repository.py
│   ├── postgres_master_resume_repository.py
│   └── postgres_scraper_runs_repository.py
├── services/
│   ├── scraper_service.py
│   ├── ai_service.py
│   ├── approval_service.py
│   ├── storage_service.py
│   └── mail_service.py  # Mail-Bridge HTTP client with 5 validation gates
├── static/
│   └── admin/
│       └── index.html   # Admin dashboard UI (Tailwind + auto-refresh)
├── tests/
│   ├── test_repositories_postgres.py
│   ├── test_scraper_routes.py
│   ├── test_ai_integration.py
│   └── test_mail_integration.py
├── requirements.txt
└── .env.example
```

---

## Database Schema

6 PostgreSQL tables created by `db/migrations/001_init_schema.sql`:

| Table | Description |
|---|---|
| `jobs` | Scraped job listings — `UNIQUE(source, external_id)` |
| `master_resumes` | User-uploaded source resumes |
| `resume_variants` | AI-generated variants — `UNIQUE(user_id, job_id)` |
| `cover_letters` | Generated cover letters |
| `application_log` | Sent applications — `UNIQUE(user_id, job_id)` |
| `scraper_runs` | Audit log for scraper executions |

Apply schema:

```bash
psql -U jobhunter -d jobhunter -f db/migrations/001_init_schema.sql
psql -U jobhunter -d jobhunter -f db/migrations/002_auth_schema.sql
```

Run Migration in container:

```bash
docker cp orchestration/db/migrations/. jobhunter-postgres:/tmp/
docker exec -it jobhunter-postgres psql -U jobhunter -d jobhunter -f /tmp/001_init_schema.sql
docker exec -it jobhunter-postgres psql -U jobhunter -d jobhunter -f /tmp/002_auth_schema.sql
```

---

## Configuration

Copy `.env.example` to `.env`.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://jobhunter:jobhunter@localhost:5432/jobhunter` | DB connection |
| `API_HOST` | `0.0.0.0` | Bind host |
| `API_PORT` | `8000` | Bind port |
| `LOG_LEVEL` | `INFO` | Log verbosity |
| `SECRET_KEY_APPROVAL` | (required) | HMAC key for approval tokens |
| `APPROVAL_TOKEN_SECRET` | (required, ≥32 chars) | HMAC-SHA256 key for email approval tokens |
| `COOKIE_SECURE` | `false` | Enforce Secure flag on refresh_token cookie (set true in production/HTTPS) |
| `MAX_APPLICATIONS_PER_DAY` | `10` | Daily application rate limit per user |
| `MAX_VARIANTS_PER_SESSION` | `15` | Per-session variant cap |
| `MAX_VARIANTS_TOTAL` | `50` | Global variant cap per user |
| `MAIL_BRIDGE_URL` | `http://localhost:3000` | Mail-Bridge service URL |
| `MAIL_BRIDGE_API_KEY` | _(empty)_ | API key for Mail-Bridge |
| `MINIO_ENDPOINT` | `minio:9000` | MinIO host:port (use `localhost:9000` locally) |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `MINIO_BUCKET_NAME` | `jobhunter-resumes` | Bucket for resume files |
| `MINIO_SECURE` | `false` | HTTPS for MinIO (set true in prod) |

---

## Mail Service

`MailService` calls Mail-Bridge over HTTP. It enforces 5 gates before sending:

1. Variant must be `approved`
2. No duplicate application for `(user_id, job_id)`
3. Daily limit not exceeded (default 10/day)
4. Minimum 30 seconds between sends
5. Job must exist, have an `apply_email`, and not be `closed`

Only on all gates passing does it call Mail-Bridge and record the application.

---

## Observability (OpenTelemetry + LGTM Stack)

The service emits OTLP traces, Prometheus metrics, and enriched JSON logs. The full backend stack lives in `DOCKER-COMPOSE.observability.yml`.

### Signal routing

| Signal | Path |
|---|---|
| Traces | `jobhunter-api` → OTLP gRPC → `otel-collector` → Tempo |
| Metrics | `jobhunter-api:/metrics` ← Prometheus scrape |
| Logs | `jobhunter-api` → OTLP → `otel-collector` → Loki |

### Auto-instrumentation

`telemetry.py` registers: `FastAPIInstrumentor` (excluding `/metrics`, `/health`), `SQLAlchemyInstrumentor`, `HTTPXClientInstrumentor`, `RedisInstrumentor`, `BotocoreInstrumentor`.

### Semantic spans

Custom spans use `async with traced("Span Name")` from `core/spans.py`:

| Span | Location |
|---|---|
| `Login` | `auth/routes/auth.py` |
| `Password Verification` | `auth/service.py` |
| `Validate Refresh Token` | `auth/service.py` |
| `Refresh Token Rotation` | `auth/service.py` |
| `Session Validation` | `auth/dependencies.py` |
| `Logout` | `auth/routes/auth.py` |
| `RBAC` | `auth/dependencies.py` |
| `Download Master Resume` | `services/ai_service.py` |
| `Run AI Pipeline` | `services/ai_service.py` |
| `Persist Variant` | `services/ai_service.py` |
| `MinIO Upload` | `api/routes/resume.py` |
| `MinIO Download Presigned URL` | `api/routes/resume.py` |

### Business metrics (`core/metrics.py`)

| Metric | Type | Description |
|---|---|---|
| `login_total` | Counter | Successful logins |
| `login_failure_total` | Counter | Failed logins with `reason` label |
| `jwt_validation_duration` | Histogram | JWT decode latency (ms) |
| `refresh_token_total` | Counter | Token rotations |
| `logout_total` | Counter | Logouts |
| `resume_upload_total` | Counter | Master resume uploads |
| `resume_generation_total` | Counter | Variant generation calls |
| `resume_generation_failed_total` | Counter | Generation failures |
| `resume_processing_duration` | Histogram | Pipeline wall-time (ms) |
| `resume_download_total` | Counter | Presigned URL generations |
| `ai_request_total` | Counter | AI invocations with `provider` label |
| `ai_request_duration` | Histogram | AI call duration (ms) |
| `ai_failure_total` | Counter | AI failures |
| `minio_upload_total` | Counter | MinIO puts with `result` label |
| `minio_download_total` | Counter | MinIO presigned downloads |

### Log enrichment (`core/logging_setup.py`)

Every JSON log record includes:
`timestamp`, `level`, `logger`, `message`, `service.name`, `environment`, `version`, `hostname`, `trace_id`, `span_id`, `business_operation` (if span active), plus optional `path`, `method`, `status_code`, `latency_ms`, `user_id`, `job_id`, `variant_id`, `req_id`, and full `stack_trace` on exceptions.

### Configuration

| Variable | Default | Description |
|---|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4317` | OTLP gRPC endpoint |

### Running the observability stack

```bash
docker compose -f DOCKER-COMPOSE.observability.yml up -d
# Grafana:    http://localhost:4000
# Prometheus: http://localhost:9090
```

---

## Admin Dashboard

Accessible at `http://localhost:8000/admin`. Auto-refreshes every 30 seconds.

- **Metrics cards:** total jobs, pending variants, sent today, total applications
- **Pending Variants tab:** copy approval token per variant
- **Recent Applications tab:** paginated application log
- **Scraper Runs tab:** last 10 runs with duration and status

---

## Docker

The `Dockerfile` installs `git` and `curl` in the base image. `curl` is required for the Docker healthcheck (`GET /health`).

```bash
docker compose up -d --build jobhunter-api
# Runs on port 8000 | healthcheck: curl http://localhost:8000/health
```

---

## Running Tests

```bash
# From project root (JobHunter/)
source orchestration/.venv/bin/activate
PYTHONPATH=. orchestration/.venv/bin/pytest orchestration/tests/ -v   # 40 tests
```

---

## Code Quality

```bash
# From project root (JobHunter/)
source orchestration/.venv/bin/activate
orchestration/.venv/bin/flake8 orchestration/ --exclude=orchestration/.venv --max-line-length=100   # 0 errors
```

---

## Authentication & RBAC

Auth is centralized in this service. Internal services (Scraper, AI Engine, Mail-Bridge) use pre-shared API keys — no JWT.

**Auth endpoints:**

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Create account |
| POST | `/api/auth/login` | Public | Login → JWT + refresh cookie |
| GET | `/api/auth/me` | Bearer JWT | Current user profile |
| PATCH | `/api/auth/me/password` | Bearer JWT | Change password |
| POST | `/api/auth/refresh` | JWT + cookie | Rotate refresh token |
| POST | `/api/auth/logout` | Bearer JWT | Revoke refresh token |

**Roles:** `hunter` · `mentor` · `recruiter` · `admin`

See [`docs/AUTH.md`](../docs/AUTH.md) for token formats and flow.  
See [`docs/RBAC.md`](../docs/RBAC.md) for role matrix and policy examples.

