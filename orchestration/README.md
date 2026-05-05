# JobHunter Orchestration API

FastAPI service that orchestrates the scraper, job inventory, and application pipeline for JobHunter Phase 0.

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
```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe — `{"status": "ok"}` |
| GET | `/readiness` | DB connectivity check |
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

---

## Directory Structure

```
orchestration/
├── api/
│   ├── main.py          # FastAPI app, middleware, lifecycle
│   ├── config.py        # Pydantic Settings (5 config classes)
│   ├── middleware.py    # RequestID, Logging, ErrorHandling, CORS
│   ├── dependencies.py  # get_db_session(), get_settings()
│   └── routes/
│       ├── scraper.py   # /api/scraper/* endpoints
    └── ai.py        # /api/ai/* endpoints (generate, pending, preview, approve, reject)
├── db/
│   ├── connection.py    # Async engine, session factory
│   ├── models.py        # SQLAlchemy ORM (6 models)
│   └── migrations/
│       └── 001_init_schema.sql
├── repositories/
│   ├── postgres_job_repository.py
│   ├── postgres_variant_repository.py
│   ├── postgres_application_repository.py
│   └── postgres_master_resume_repository.py
├── services/
│   ├── scraper_service.py
│   ├── ai_service.py       # AIService — wraps AI Engine pipeline
│   ├── approval_service.py # ApprovalService — HMAC-SHA256 token flow
│   └── storage_service.py  # StorageService — Phase 0 local file stub
├── core/                # Reserved for Phase 1
├── static/              # Reserved for Phase 1
├── tests/
│   ├── test_repositories_postgres.py
│   ├── test_scraper_routes.py
│   └── test_ai_integration.py
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

Copy `.env.example` to `.env`. All variables have defaults except `SECRET_KEY_APPROVAL`.

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
| `SCRAPER_OUTPUT_DIR` | `./output/final` | Scraper output directory |

---

## Repository Implementations

The three PostgreSQL repositories implement the abstract interfaces from `jobhunter-dpl`:

| Class | Interface | Methods |
|---|---|---|
| `PostgresJobRepository` | `JobRegistryBase` | 9 async methods — save (upsert), get, get_many, get_by_source, get_by_status, get_all_with_email, exists, count, delete_by_source |
| `PostgresVariantRepository` | `VariantRegistryBase` | 10 async methods — save, get, get_for_job, get_approved_for_job, get_for_user, get_pending_for_user, update_approval_status, update_approval_token, exists, count_by_user |
| `PostgresApplicationRepository` | `ApplicationLogBase` | 9 async methods — record_send, get, get_by_user, get_by_job, has_user_applied_to_job, get_applications_sent_today, update_status, update_reply_count, count_by_user |
| `PostgresMasterResumeRepository` | — | `get_or_create(user_id, file_path)` — parse and persist master resume |

**Constraints enforced:**
- One variant per `(user_id, job_id)` — raises `RegistryError` on duplicate
- Max 50 variants per user — raises `RegistryError` on cap exceeded
- One application per `(user_id, job_id)` — raises `RegistryError` on duplicate

---

## AI Service Layer

`AIService` wraps the AI Engine pipeline for single-job variant generation.

| Class | File | Responsibility |
|---|---|---|
| `AIService` | `services/ai_service.py` | Orchestrates resume parse → job analysis → optimise → store |
| `ApprovalService` | `services/approval_service.py` | HMAC-SHA256 token generation, validation, mark_approved |
| `StorageService` | `services/storage_service.py` | Phase 0 local file copy stub |

### Approval Token Flow

```
POST /api/ai/generate
  ↓ AIService.generate_variant()
  ↓ ApprovalService.generate_approval_token()  → token stored on VariantRecord
  ↓ Response includes approval_link

POST /api/ai/approve/{variant_id}?token=...
  ↓ ApprovalService.validate_approval_token()  → HMAC verify + expiry check
  ↓ ApprovalService.mark_approved()           → status=approved, approved_at set in DB
```

Token format: `{variant_id}:{unix_timestamp}:{base64_hmac_sha256}`  
TTL: 24 hours. Single-use (rejected/approved variants cannot be re-approved).

---

## Running Tests

```bash
cd orchestration/
PYTHONPATH=.. .venv/bin/pytest tests/ -v   # 31 tests
```

---

## Code Quality

```bash
.venv/bin/flake8 . --exclude=.venv --max-line-length=100   # 0 errors
```
