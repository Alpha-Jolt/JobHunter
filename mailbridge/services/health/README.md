# @mail-bridge/health

## Overview

Liveness and readiness health check microservice for Mail-Bridge. Provides two endpoints used by Docker health checks, load balancers, and monitoring systems. No authentication required.

## Key Capabilities

- **Liveness** — always returns 200 if the process is running
- **Readiness** — checks both PostgreSQL and Redis connectivity; returns 503 if either is down

## Quick Start

```bash
cd services/health
cp .env.example .env
npm run dev   # starts on :3006
```

## API Reference

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | Public | Liveness — always 200 |
| GET | `/health/ready` | Public | Readiness — 200 if DB+Redis ok, 503 if not |

### GET `/health`
```json
{ "status": "ok", "version": "2.0.0", "timestamp": "2026-05-23T09:00:00.000Z" }
```

### GET `/health/ready`
```json
// 200 — healthy
{ "status": "ready", "db": "ok", "redis": "ok" }

// 503 — degraded
{ "status": "not_ready", "db": "down", "redis": "ok" }
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3006` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, DB pool, Redis client

## Integration

Used by `docker-compose.yml` health checks for all services:
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3006/health"]
```
