# @mail-bridge/admin

## Overview

Workspace administration microservice for Mail-Bridge. Provides user management operations (invite, role change, soft-delete) scoped to a workspace. Only `owner` role (Free/Pro) or `operational-admin`+ (Enterprise) can access these endpoints.

## Key Capabilities

- **List users** — all active workspace members
- **Invite user** — creates user record with `INVITE_PENDING` password placeholder
- **Change role** — update a user's flat role (`owner`/`member`)
- **Remove user** — soft-delete (sets `deleted_at`; data preserved)

## Quick Start

```bash
cd services/admin
cp .env.example .env
npm run dev   # starts on :3005
```

## API Reference

| Method | Path | Role | API Key Scope | Description |
|---|---|---|---|---|
| GET | `/api/admin/users` | owner | `admin` | List all users in the workspace |
| POST | `/api/admin/users` | owner | `admin` | Invite a new user to the workspace |
| PUT | `/api/admin/users/:id/role` | owner | `admin` | Change a user's role |
| DELETE | `/api/admin/users/:id` | owner | `admin` | Remove a user from the workspace |

### POST `/api/admin/users`
```json
Request:  { "email": "newmember@example.com", "role": "member" }
Response: { "success": true, "user": { "user_id": "uuid", "email": "...", "role": "member", ... } }
```

### PUT `/api/admin/users/:id/role`
```json
Request:  { "role": "owner" }
Response: { "success": true }
```

**Error codes:** `INVALID_PAYLOAD` · `USER_EXISTS` · `NOT_FOUND` · `MISSING_TOKEN` · `INVALID_TOKEN` · `INSUFFICIENT_ROLE`

**Note:** `password_hash` is never returned in any response.

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3005` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis (auth blocklist check) |
| `JWT_SECRET` | Yes | — | JWT verification |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, auth middleware, authz middleware, DB pool

## Testing

```bash
npm test -- tests/unit
npm test -- tests/integration
npm run test:coverage
```
