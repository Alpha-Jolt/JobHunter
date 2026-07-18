# @mail-bridge/templates

## Overview

Email template management microservice for Mail-Bridge. Provides CRUD operations for reusable Handlebars email templates scoped to a workspace. Templates are referenced by `template_id` in the emails service send request.

## Key Capabilities

- **Create/update/delete** templates with name, subject, html, and variable list
- **Custom variable validation** — define `required`, `maxLength`, `pattern` rules per template; enforced at send time
- **Version tracking** — `version` increments on every update; previous state snapshotted to `email_template_versions`
- **Version history** — paginated `GET /api/templates/:id/versions`
- **Rollback** — restore any previous version; creates a new version (history never rewritten)
- **Workspace isolation** — templates are scoped to the authenticated user's workspace

## Quick Start

```bash
cd services/templates
cp .env.example .env
npm run dev   # starts on :3004
```

## API Reference

| Method | Path | Role | API Key Scope | Description |
|---|---|---|---|---|
| POST | `/api/templates` | member | `templates` | Create a new template |
| GET | `/api/templates` | member | `templates` | List all templates for workspace |
| PUT | `/api/templates/:id` | member | `templates` | Update template (creates new version) |
| GET | `/api/templates/:id/versions` | member | `templates` | List version history for a template |
| POST | `/api/templates/:id/rollback` | member | `templates` | Rollback to a previous version |
| DELETE | `/api/templates/:id` | member | `templates` | Soft-delete template |

### POST `/api/templates`
```json
Request: {
  "name": "Welcome Email",
  "subject": "Welcome {{name}}",
  "html": "<p>Hi {{name}}, welcome to {{company}}!</p>",
  "variables": ["name", "company"],
  "validation_rules": { "required": ["name"], "maxLength": { "subject": 100 } }
}
Response: { "success": true, "template": { "template_id": "uuid", "name": "...", "version": 1, ... } }
```

### POST `/api/templates/:id/rollback`
```json
Request:  { "version": 1 }
Response: { "success": true, "template": { ..., "version": 3 } }
```
> Rollback creates a new version — history is never rewritten.

### PUT `/api/templates/:id`
```json
Request: { "name": "Updated Name" }   // partial update — only provided fields change
Response: { "success": true, "template": { ..., "version": 2 } }
```

**Error codes:** `INVALID_PAYLOAD` · `NOT_FOUND` · `MISSING_TOKEN` · `INVALID_TOKEN`

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `3004` | Service port |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis (auth blocklist check) |
| `JWT_SECRET` | Yes | — | JWT verification |
| `LOG_LEVEL` | No | `info` | Pino log level |

## Dependencies

### Required
- `@mail-bridge/shared` — logger, errors, auth middleware, DB pool

## Testing

```bash
npm test -- tests/unit
npm test -- tests/integration
npm run test:coverage
```
