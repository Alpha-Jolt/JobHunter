# Shared Registry Service

FastAPI adapter that exposes the `shared/` Python library as a language-agnostic REST API on port **8003**.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/health/ready` | Readiness check |
| GET | `/api/jobs/{job_id}` | Get job by ID |
| GET | `/api/jobs/by-source/{source}` | List jobs by source |
| GET | `/api/jobs/status/{status}` | List jobs by status |
| GET | `/api/jobs/all-with-email` | List jobs with apply_email set |
| GET | `/api/variants/{variant_id}` | Get variant by ID |
| GET | `/api/variants/approved/{job_id}/{user_id}` | Get approved variant (Mail-Bridge) |
| GET | `/api/variants/for-user/{user_id}` | List variants for user |
| POST | `/api/variants` | Create variant |
| PATCH | `/api/variants/{variant_id}/approval` | Update approval status |
| GET | `/api/applications/{application_id}` | Get application by ID |
| GET | `/api/applications/by-user/{user_id}` | List applications for user |
| GET | `/api/applications/by-job/{job_id}` | List applications for job |
| GET | `/api/applications/sent-today/{user_id}` | Applications sent in last 24h |
| POST | `/api/applications` | Record new application |
| PATCH | `/api/applications/{application_id}/status` | Update application status |
| GET | `/api/files/signed-url` | Generate MinIO presigned URL |

## Auth

All endpoints except `/health` require: `Authorization: Bearer <API_KEY_TOKEN>`

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --host 0.0.0.0 --port 8003 --reload
```

## Tests

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

## Docker

```bash
docker compose -f ../../DOCKER-COMPOSE.yml up -d shared-registry-service
```
