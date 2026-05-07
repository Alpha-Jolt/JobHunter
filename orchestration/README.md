# JobHunter Orchestration API

FastAPI service that orchestrates the scraper, job inventory, AI resume pipeline, mail sending, and admin monitoring for JobHunter Phase 0.

> **Port:** 8000 | **Phase:** 0 | **Status:** Complete

---

## Quick Start

```bash
cd orchestration/
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
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
│       ├── mail.py      # /api/mail/* endpoints
│       ├── admin.py     # /api/admin/* endpoints
│       └── health.py    # /health and /readiness endpoints
├── core/
│   ├── exceptions.py    # Domain exceptions (ApprovalRequiredError, MailSendError, etc.)
│   └── logging_setup.py # Structured JSON logging
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
| `MAX_APPLICATIONS_PER_DAY` | `10` | Daily application rate limit per user |
| `MAX_VARIANTS_PER_SESSION` | `15` | Per-session variant cap |
| `MAX_VARIANTS_TOTAL` | `50` | Global variant cap per user |
| `MAIL_BRIDGE_URL` | `http://localhost:3000` | Mail-Bridge service URL |
| `MAIL_BRIDGE_API_KEY` | _(empty)_ | API key for Mail-Bridge |

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

## Admin Dashboard

Accessible at `http://localhost:8000/admin`. Auto-refreshes every 30 seconds.

- **Metrics cards:** total jobs, pending variants, sent today, total applications
- **Pending Variants tab:** copy approval token per variant
- **Recent Applications tab:** paginated application log
- **Scraper Runs tab:** last 10 runs with duration and status

---

## Running Tests

```bash
cd orchestration/
PYTHONPATH=.. .venv/bin/pytest tests/ -v   # 40 tests
```

---

## Code Quality

```bash
.venv/bin/flake8 . --exclude=.venv --max-line-length=100   # 0 errors
```
