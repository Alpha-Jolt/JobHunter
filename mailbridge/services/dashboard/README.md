# @mail-bridge/dashboard

## Overview

Server-rendered status dashboard microservice for Mail-Bridge. Provides a single authenticated HTML page showing workspace stats and recent email activity. No frontend build step — HTML is generated inline by the Express route, following the same pattern as Mail-Bridge v1.

## Key Capabilities

- **Workspace overview** — name, tier, active credential count, emails sent today
- **Recent email log** — last 10 sends with to, subject, status, and timestamp
- **No build step** — pure server-rendered HTML; no React, no bundler
- **JWT-protected** — requires valid Bearer token; shows workspace-scoped data only

## Quick Start

```bash
cd services/dashboard
cp .env.example .env
npm run dev   # starts on :3007
```

Visit `http://localhost:3007/` with a valid JWT in the `Authorization` header, or use a browser extension to set the header.

## API Reference

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Bearer | Server-rendered HTML dashboard |

Returns `text/html` — not JSON.

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3007` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis (auth blocklist check) |
| `JWT_SECRET` | Yes | — | JWT verification |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, auth middleware, DB pool

## Known Limitations

- Phase 0: dashboard is server-rendered HTML only
- Phase 1+: React frontend will replace this with a full SPA
- No real-time updates — page must be refreshed manually
