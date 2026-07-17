# @mail-bridge/auth

## Overview

Authentication microservice for Mail-Bridge. Handles user registration, login, logout, and JWT token refresh. Passwords are hashed with Argon2; tokens are blocklisted in Redis on logout to prevent reuse.

## Key Capabilities

- **Register** — creates user + workspace in a single transaction; returns JWT and default API key
- **Login** — verifies Argon2 password hash; returns JWT with `{ user_id, workspace_id, tier, role }`
- **Logout** — blocklists token in Redis with TTL equal to remaining token lifetime
- **Refresh** — issues new JWT from a valid existing token
- **API Keys** — creates, lists, and revokes API keys for headless API access
- **Input validation** — email format, password minimum length enforced before DB access

## Quick Start

```bash
cd services/auth
cp .env.example .env   # or set env vars
npm run dev            # starts on :3001
```

## API Reference

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Create account + workspace |
| POST | `/auth/login` | Public | Returns JWT |
| POST | `/auth/logout` | Bearer | Blocklists token |
| POST | `/auth/refresh` | Public | Returns new JWT |
| POST | `/auth/upgrade` | Bearer | Upgrade workspace to Pro |
| POST | `/auth/api-keys` | Bearer (owner) | Create an API key |
| GET | `/auth/api-keys` | Bearer (owner) | List API keys |
| DELETE | `/auth/api-keys/:id` | Bearer (owner) | Revoke an API key |

### POST `/auth/register`
```json
Request:  { "email": "user@example.com", "password": "Password123!", "workspace_name": "My Team" }
Response: { "success": true, "user_id": "uuid", "workspace_id": "uuid", "token": "jwt", "expires_at": "ISO8601" }
```

### POST `/auth/login`
```json
Request:  { "email": "user@example.com", "password": "Password123!" }
Response: { "success": true, "token": "jwt", "expires_at": "ISO8601" }
```

### POST `/auth/logout`
```
Header: Authorization: Bearer <token>
Response: { "success": true }
```

### POST `/auth/refresh`
```json
Request:  { "token": "existing-jwt" }
Response: { "success": true, "token": "new-jwt", "expires_at": "ISO8601" }
```

### POST `/auth/upgrade`
```
Header:   Authorization: Bearer <token>
Response: { "success": true, "token": "new-jwt", "expires_at": "ISO8601" }
```

**Error codes:** `INVALID_PAYLOAD` · `INVALID_EMAIL` · `WEAK_PASSWORD` · `EMAIL_EXISTS` · `INVALID_CREDENTIALS` · `MISSING_TOKEN` · `INVALID_TOKEN` · `TOKEN_REVOKED`

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3001` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis for token blocklist |
| `JWT_SECRET` | Yes | — | Min 32 chars |
| `JWT_EXPIRES_IN` | No | `24h` | Token lifetime |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, DB pool, Redis client
- `argon2 0.31.2` — password hashing
- `jsonwebtoken 9.0.2` — JWT signing/verification
- `express 4.18.2` — HTTP server

## Testing

```bash
npm test -- tests/unit        # 6 unit tests, no DB/Redis needed
npm test -- tests/integration # requires mailbridge_test DB + Redis
npm run test:coverage
```

Unit tests cover: register success/conflict, login wrong password/unknown email, refresh valid/invalid token.
