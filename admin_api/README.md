# JobHunter Admin API

FastAPI backend for the JobHunter Admin Console. Provides authentication, scraper control, and audit logging for the admin interface.

> **Port:** 8003 | **Phase:** 1 | **Status:** Complete

---

## Quick Start

```bash
cd admin_api/
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD_HASH
uvicorn app:app --reload --port 8003
# Swagger UI: http://localhost:8003/docs
```

---

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | Public | Liveness probe — `{"status": "ok"}` |
| POST | `/auth/login` | Public | Login with email + password → JWT + refresh cookie |
| POST | `/auth/refresh` | Cookie | Rotate refresh token |
| POST | `/auth/logout` | Bearer JWT | Revoke refresh token |
| POST | `/scraper/trigger` | Bearer JWT | Enqueue a scraper task to Redis |
| GET | `/scraper/status` | Bearer JWT | Current scraper status from Redis |
| GET | `/scraper/logs` | Bearer JWT | Stream recent scraper log lines |

---

## Directory Structure

```
admin_api/
├── app.py               # FastAPI app — lifespan, router registration
├── auth/
│   ├── __init__.py
│   ├── router.py        # /auth/* endpoints — login, refresh, logout, lockout
│   ├── service.py       # Argon2 verify, JWT encode/decode
│   ├── models.py        # LoginRequest (EmailStr + password), TokenResponse
│   └── dependencies.py  # require_admin_session — HTTPBearer guard
├── core/
│   ├── __init__.py
│   ├── config.py        # Pydantic Settings — all env vars
│   ├── redis.py         # get_redis() — single async Redis client
│   ├── security.py      # SecurityHeadersMiddleware
│   └── rate_limit.py    # slowapi limiter setup
├── scraper/
│   ├── __init__.py
│   ├── router.py        # /scraper/* endpoints
│   ├── service.py       # Audit hash chaining, preferences DB save, Redis enqueue
│   └── models.py        # ScraperPreferences, ScraperAuditLog ORM models
├── tests/
│   ├── __init__.py
│   └── test_security.py # Unauthorized trigger → 401, health → 200
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## Configuration

Copy `.env.example` to `.env`.

| Variable | Description |
|---|---|
| `ENVIRONMENT` | `development` or `production` |
| `SECRET_KEY` | JWT signing secret — minimum 32 chars, random |
| `ADMIN_EMAIL` | Admin login email |
| `ADMIN_PASSWORD_HASH` | Argon2id hash of the admin password |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `POSTGRES_URL` | `postgresql+asyncpg://jobhunter:jobhunter@postgres:5432/jobhunter` |
| `REDIS_URL` | `redis://redis:6379/0` |
| `FRONTEND_URL` | CORS allowed origin — `http://localhost:5001` |

### Generating the Admin Password Hash

```python
from argon2 import PasswordHasher
print(PasswordHasher().hash("your-password-here"))
```

---

## Security

- **Argon2id** password hashing (not bcrypt)
- **JWT** access tokens (15 min) + refresh tokens via httpOnly cookie (7 days)
- **Rate limiting** via `slowapi` — login endpoint is strictly limited
- **Account lockout** after 10 consecutive failed login attempts
- **Audit log** — hash-chained, append-only, stores user ID, request ID, and timestamp on every scraper trigger
- **Security headers** — X-Frame-Options, X-Content-Type-Options, CSP via middleware

---

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## Docker

```bash
docker compose up -d --build admin-api
# Runs on port 8003 internally; not directly exposed in production
```
