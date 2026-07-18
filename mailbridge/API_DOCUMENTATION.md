# Mail-Bridge — API Documentation

**Version**: 2.0.0  
**Base URL**: `http://localhost:3009` (Nginx gateway)  
**Protocol**: HTTP/1.1  
**Content-Type**: `application/json` (all requests and responses)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Format](#error-format)
5. [Auth Service](#auth-service)
6. [Credentials Service](#credentials-service)
7. [Emails Service](#emails-service)
8. [Templates Service](#templates-service)
9. [Webhooks Service](#webhooks-service)
10. [Admin Service](#admin-service)
11. [Health Service](#health-service)
12. [Dashboard Service](#dashboard-service)
13. [Webhook Event Delivery](#webhook-event-delivery)
14. [Data Models](#data-models)
15. [Internal Architecture](#internal-architecture)
16. [How-To Guide](#how-to-guide)

---

## Overview

Mail-Bridge is a multi-tenant email delivery platform. All external traffic passes through the Nginx gateway on port **3009**. Services are not directly accessible from outside the Docker network.

### Service Map

| Service | Internal Port | Gateway Prefix |
|---|---|---|
| Auth | 3001 | `/auth/` |
| Credentials | 3002 | `/api/credentials/` |
| Emails | 3003 | `/api/emails/` |
| Templates | 3004 | `/api/templates/` |
| Admin | 3005 | `/api/admin/` |
| Health | 3006 | `/health` |
| Dashboard | 3007 | (internal HTML, no gateway route) |
| Webhooks | 3008 | `/api/webhooks/` |

> **Note**: The `dashboard` service (port 3007) renders an HTML status page and has no gateway route. Access it directly in development or wire a gateway route if needed.

### URL Construction

All examples use the gateway base URL `http://localhost:3009`.

```
http://localhost:3009/auth/register
http://localhost:3009/api/emails/send
http://localhost:3009/api/webhooks/
```

---

## Authentication

Mail-Bridge supports two authentication methods depending on the route and caller:

1. **Bearer JWT**: Used for the Management Console (Webapp).
2. **API Keys**: Used for programmatic headless access (REST API).

### 1. Bearer JWT

Required for Management Console routes. Passed in the `Authorization` header.

```
Authorization: Bearer <token>
```

Tokens are obtained from `POST /auth/login` or `POST /auth/register`. They expire in **24 hours** (configurable via `JWT_EXPIRES_IN`).

### JWT Payload

```json
{
  "user_id": "uuid",
  "workspace_id": "uuid",
  "tier": "free | pro | enterprise",
  "role": "owner | member",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234654290,
  "jti": "uuid"
}
```

### Role Hierarchy

**Free / Pro tiers** use flat roles:

| Role | Level | Can access |
|---|---|---|
| `member` | 0 | Emails, Templates, Scheduled emails |
| `owner` | 1 | Everything member can + Credentials, Webhooks, Admin |

**Enterprise tier** uses RBAC via `workspace_roles` table:

| Role | Level |
|---|---|
| `user` | 0 |
| `admin` | 1 |
| `operational-admin` | 2 |
| `system-admin` | 3 |

### Token Blocklist

Logged-out tokens are stored in Redis under `blocklist:<token>` until their natural expiry. The `authenticate` middleware checks this on every request.

### 2. API Keys

API keys are required for headless operations and programmatic integrations (e.g. from JobHunter). Passed in the `Authorization` header.

```
Authorization: Bearer sk_...
```

**Prefixes:**
- `sk_`: Production keys
- `sk_test_`: Non-production (development/testing) keys

API keys support scope-based access (e.g., `send`, `read`, `templates`, `credentials`, `admin`). Keys with missing scopes will be rejected with a `403 Forbidden` (`INSUFFICIENT_SCOPE`). 
Note: API Keys **cannot** be used to manage other API keys. The `/api-keys` endpoints strictly require a Bearer JWT.

---

## Rate Limiting

Enforced by Nginx. Limits are per **IP address**.

| Zone | Applies to | Rate | Burst | Behavior on exceed |
|---|---|---|---|---|
| `auth_limit` | `/auth/*` | 5 req/min | 3 | 429 Too Many Requests |
| `api_limit` | `/api/*` | 100 req/sec | varies | 429 Too Many Requests |

### Per-route burst values

| Route prefix | Burst |
|---|---|
| `/api/credentials/` | 20 |
| `/api/emails/` | 50 |
| `/api/templates/` | 20 |
| `/api/admin/` | 10 |
| `/api/webhooks/` | 20 |

### Gateway-injected Headers

Every proxied request receives:

| Header | Value |
|---|---|
| `X-Device-Fingerprint` | Hash of `$remote_addr + $http_user_agent` |
| `X-Real-IP` | Client IP |
| `X-Forwarded-For` | Proxy chain |

---

## Error Format

All error responses follow this shape:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

### HTTP Status Codes

| Status | When |
|---|---|
| 400 | Validation failure (`INVALID_PAYLOAD`, `WEAK_PASSWORD`, `INVALID_EMAIL`, etc.) |
| 401 | Missing/invalid/expired/revoked token |
| 403 | Insufficient role or tier |
| 404 | Resource not found |
| 409 | Conflict (duplicate email, existing user, etc.) |
| 429 | Rate limit exceeded (returned by Nginx) |
| 502 | External provider failure (OAuth, SMTP) |
| 500 | Unexpected internal error |

### Error Codes Reference

| Code | Status | Description |
|---|---|---|
| `INVALID_PAYLOAD` | 400 | Missing or malformed required fields |
| `INVALID_EMAIL` | 400 | Email format invalid |
| `WEAK_PASSWORD` | 400 | Password under 8 characters |
| `VALIDATION_FAILED` | 400 | Template variable validation failed |
| `BATCH_TOO_LARGE` | 400 | Batch size exceeds `BATCH_MAX_SIZE` (default 100) |
| `MISSING_CODE` | 400 | OAuth callback missing `code` param |
| `MISSING_TOKEN` | 401 | Authorization header absent |
| `INVALID_TOKEN` | 401 | JWT malformed or expired |
| `TOKEN_REVOKED` | 401 | Token blocklisted (logged out) |
| `INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `FORBIDDEN` | 403 | Owner-only operation attempted by non-owner |
| `ALREADY_UPGRADED` | 403 | Workspace already on pro or higher |
| `INSUFFICIENT_ROLE` | 403 | Role below required level |
| `INSUFFICIENT_TIER` | 403 | Tier below required level |
| `NOT_FOUND` | 404 | Resource absent or not owned by workspace |
| `EMAIL_EXISTS` | 409 | Email already registered |
| `USER_EXISTS` | 409 | User already exists in workspace |
| `OAUTH_FAILED` | 502 | Provider OAuth returned no access token |
| `INTERNAL_ERROR` | 500 | Unhandled exception |

---
## Auth Service

**Base path**: `/auth`  
**Internal port**: `3001`  
**Rate limit**: 5 req/min per IP, burst 3

---

### POST /auth/register

Create a new user account and workspace. The registering user becomes the workspace `owner`.

**Auth required**: No

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Minimum 8 characters |
| `workspace_name` | string | Yes | Display name for the new workspace |

**Example request**:

```json
{
  "email": "alice@example.com",
  "password": "securepass123",
  "workspace_name": "Acme Corp"
}
```

**Response** `201 Created`:

```json
{
  "success": true,
  "user_id": "d4e5f6a7-...",
  "workspace_id": "a1b2c3d4-...",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2026-06-03T14:02:50.000Z"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | Any required field missing |
| `INVALID_EMAIL` | Email format invalid |
| `WEAK_PASSWORD` | Password shorter than 8 chars |
| `EMAIL_EXISTS` | Email already registered |

---

### POST /auth/login

Authenticate and receive a JWT.

**Auth required**: No

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | Registered email |
| `password` | string | Yes | Account password |

**Example request**:

```json
{
  "email": "alice@example.com",
  "password": "securepass123"
}
```

**Response** `200 OK`:

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2026-06-03T14:02:50.000Z"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | Missing email or password |
| `INVALID_CREDENTIALS` | Wrong email or password |

---

### POST /auth/logout

Invalidate the current token by adding it to the Redis blocklist.

**Auth required**: Yes (Bearer token)

**Request body**: None

**Response** `200 OK`:

```json
{ "success": true }
```

---

### POST /auth/refresh

Exchange a still-valid token for a new one with a fresh expiry.

**Auth required**: No (token passed in body, not header)

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `token` | string | Yes | A currently valid JWT |

**Example request**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** `200 OK`:

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2026-06-04T14:02:50.000Z"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `token` field missing |
| `INVALID_TOKEN` | Token expired or malformed |

---

### POST /auth/upgrade

Upgrade the authenticated user's workspace from `free` to `pro`. Returns a new token with `tier: "pro"`.

**Auth required**: Yes — `owner` role required

**Request body**: None

**Response** `200 OK`:

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2026-06-04T14:02:50.000Z"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `FORBIDDEN` | Caller is not workspace owner |
| `ALREADY_UPGRADED` | Workspace tier is already `pro` or `enterprise` |

---
## Credentials Service

**Base path**: `/api/credentials`  
**Internal port**: `3002`  
**Rate limit**: 100 req/sec, burst 20  
**Auth required**: Yes — `owner` role required on all endpoints  

Credentials store encrypted provider tokens (Gmail OAuth 2.0, Outlook OAuth 2.0, SMTP). Sensitive values are AES-256-GCM encrypted at rest using `CREDENTIAL_MASTER_KEY`. The encrypted payload is never returned in API responses.

---

### GET /api/credentials/gmail/connect

Generate a Gmail OAuth 2.0 authorization URL. Redirect the user's browser to this URL to begin the OAuth flow.

**Response** `200 OK`:

```json
{
  "success": true,
  "url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

> The OAuth consent URL includes `access_type=offline` and `prompt=consent` to ensure a refresh token is issued.

---

### GET /api/credentials/gmail/callback

OAuth 2.0 callback endpoint. Google redirects here after user consent. Stores the encrypted tokens and fetches the Gmail address via the Gmail API.

**Query parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `code` | string | Yes | Authorization code from Google |
| `state` | string | Yes | Workspace ID (set during connect) |

**Response** `200 OK`:

```json
{
  "success": true,
  "credential_id": "uuid",
  "from_email": "alice@gmail.com"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `MISSING_CODE` | `code` query param absent |
| `OAUTH_FAILED` | Google returned no access token |

---

### GET /api/credentials/outlook/connect

Generate a Microsoft Outlook OAuth 2.0 authorization URL.

**Response** `200 OK`:

```json
{
  "success": true,
  "url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?..."
}
```

---

### GET /api/credentials/outlook/callback

OAuth 2.0 callback for Outlook. Stores tokens and fetches the user's email via Microsoft Graph API (`/me`).

**Query parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `code` | string | Yes | Authorization code from Microsoft |
| `state` | string | Yes | Workspace ID |

**Response** `200 OK`:

```json
{
  "success": true,
  "credential_id": "uuid",
  "from_email": "alice@outlook.com"
}
```

---

### POST /api/credentials/smtp

Add an SMTP credential.

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `from_email` | string | Yes | Sender email address |
| `host` | string | Yes | SMTP server hostname |
| `port` | number | Yes | SMTP port (e.g. 587, 465, 25) |
| `secure` | boolean | No | Use TLS (`true` = port 465 style) |
| `user` | string | Yes | SMTP username |
| `pass` | string | Yes | SMTP password |

**Example request**:

```json
{
  "from_email": "noreply@example.com",
  "host": "smtp.example.com",
  "port": 587,
  "secure": false,
  "user": "noreply@example.com",
  "pass": "smtp-password"
}
```

**Response** `201 Created`:

```json
{
  "success": true,
  "credential_id": "uuid",
  "workspace_id": "uuid",
  "provider_type": "smtp",
  "from_email": "noreply@example.com",
  "is_active": true,
  "last_used_at": null,
  "metadata": {},
  "created_at": "2026-06-02T14:02:50.000Z",
  "encryption_key_id": "uuid"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | Any of `from_email`, `host`, `port`, `user`, `pass` missing |

---

### GET /api/credentials/

List all active credentials for the workspace. `encrypted_value` is never included.

**Response** `200 OK`:

```json
{
  "success": true,
  "credentials": [
    {
      "credential_id": "uuid",
      "workspace_id": "uuid",
      "provider_type": "gmail",
      "from_email": "alice@gmail.com",
      "is_active": true,
      "last_used_at": null,
      "metadata": {},
      "created_at": "2026-06-02T14:02:50.000Z",
      "encryption_key_id": "uuid"
    }
  ]
}
```

---

### DELETE /api/credentials/:id

Soft-delete a credential (sets `is_active = false`). The credential record is retained in the database.

**Path parameter**: `id` — credential UUID

**Response** `200 OK`:

```json
{ "success": true }
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Credential not found or not owned by workspace |

---

### POST /api/credentials/:id/test

Verify a credential is decryptable (accessible). Does not send a test email.

**Path parameter**: `id` — credential UUID

**Response** `200 OK`:

```json
{
  "success": true,
  "message": "Credential is valid and accessible"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Credential not found or inactive |

---
## Emails Service

**Base path**: `/api/emails`  
**Internal port**: `3003`  
**Rate limit**: 100 req/sec, burst 50  
**Auth required**: Yes — `member` role minimum (owners also qualify)

The emails service enqueues jobs to a Redis FIFO queue (`mail:queue`). A worker loop processes jobs with up to **3 automatic retries**. On final failure the email log status is set to `failed` and a `email.failed` webhook event is published.

---

### POST /api/emails/send

Queue a single email for delivery. Returns immediately with `status: "queued"`.

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `credential_id` | string (UUID) | Yes | Credential to send from |
| `to_email` | string | Yes | Recipient email address |
| `subject` | string | Conditional | Required if `template_id` not provided |
| `html` | string | Conditional | HTML body. Required if `template_id` not provided |
| `template_id` | string (UUID) | Conditional | Use a saved template (overrides `subject`/`html`) |
| `variables` | object | No | Handlebars variables injected into subject and HTML |
| `attachments` | array | No | List of `{ filename: string, url: string }` objects to attach |

> Either (`subject` + `html`) or `template_id` must be provided.

**Example — direct HTML**:

```json
{
  "credential_id": "a1b2c3d4-...",
  "to_email": "bob@example.com",
  "subject": "Hello {{name}}",
  "html": "<p>Hi {{name}}, welcome!</p>",
  "variables": { "name": "Bob" }
}
```

**Example — using a template**:

```json
{
  "credential_id": "a1b2c3d4-...",
  "to_email": "bob@example.com",
  "template_id": "e5f6a7b8-...",
  "variables": { "name": "Bob", "company": "Acme" }
}
```

**Example — with attachment**:

```json
{
  "credential_id": "a1b2c3d4-...",
  "to_email": "bob@example.com",
  "subject": "Your invoice",
  "html": "<p>See attached.</p>",
  "attachments": [
    { "filename": "invoice.pdf", "url": "https://cdn.example.com/invoice-123.pdf" }
  ]
}
```

**Response** `202 Accepted`:

```json
{
  "success": true,
  "email_id": "uuid",
  "status": "queued"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `credential_id` or `to_email` missing; or both `subject`/`html` and `template_id` absent |
| `NOT_FOUND` | `credential_id` not found / inactive, or `template_id` not found |
| `VALIDATION_FAILED` | Template variables fail `validation_rules` |

---

### POST /api/emails/batch

Queue multiple emails in a single request. Each email is individually queued.

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `emails` | array | Yes | Array of `SendEmailInput` objects (same shape as `/send`) |

Maximum batch size is controlled by `BATCH_MAX_SIZE` environment variable (default: **100**).

**Example request**:

```json
{
  "emails": [
    {
      "credential_id": "a1b2c3d4-...",
      "to_email": "alice@example.com",
      "subject": "Welcome",
      "html": "<p>Hi Alice!</p>"
    },
    {
      "credential_id": "a1b2c3d4-...",
      "to_email": "bob@example.com",
      "subject": "Welcome",
      "html": "<p>Hi Bob!</p>"
    }
  ]
}
```

**Response** `202 Accepted`:

```json
{
  "success": true,
  "queued": 2,
  "email_ids": ["uuid-1", "uuid-2"]
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `emails` array is empty |
| `BATCH_TOO_LARGE` | Array length exceeds `BATCH_MAX_SIZE` |

---

### POST /api/emails/schedule

Schedule an email for future delivery.

**Request body**: Same fields as `/send`, plus:

| Field | Type | Required | Description |
|---|---|---|---|
| `scheduled_at` | string (ISO 8601) | Yes | Future UTC datetime for delivery |

**Example request**:

```json
{
  "credential_id": "a1b2c3d4-...",
  "to_email": "bob@example.com",
  "subject": "Reminder",
  "html": "<p>Don't forget!</p>",
  "scheduled_at": "2026-06-10T09:00:00.000Z"
}
```

**Response** `201 Created`:

```json
{
  "success": true,
  "scheduled_id": "uuid",
  "scheduled_at": "2026-06-10T09:00:00.000Z"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `scheduled_at` missing, not a valid date, or in the past |

---

### GET /api/emails/schedule

List pending scheduled emails for the workspace.

**Query parameters**:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | number | 1 | Page number (1-based) |
| `limit` | number | 20 | Items per page |

**Response** `200 OK`:

```json
{
  "success": true,
  "scheduled": [
    {
      "scheduled_id": "uuid",
      "to_email": "bob@example.com",
      "subject": "Reminder",
      "scheduled_at": "2026-06-10T09:00:00.000Z",
      "status": "pending",
      "created_at": "2026-06-02T14:02:50.000Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

---

### GET /api/emails/stats

Get high-level status breakdown of all emails in the workspace.

**Response** `200 OK`:

```json
{
  "success": true,
  "stats": {
    "total": 105,
    "sent": 95,
    "failed": 8,
    "queued": 2,
    "today": 12
  }
}
```

---

### DELETE /api/emails/schedule/:id

Cancel a pending scheduled email.

**Path parameter**: `id` — scheduled email UUID

**Response** `200 OK`:

```json
{ "success": true }
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Scheduled email not found, not owned by workspace, or already processed/cancelled |

---

### GET /api/emails/

List all email logs for the workspace, newest first.

**Query parameters**:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | number | 1 | Page number |
| `limit` | number | 20 | Items per page |

**Response** `200 OK`:

```json
{
  "success": true,
  "emails": [
    {
      "email_id": "uuid",
      "workspace_id": "uuid",
      "credential_id": "uuid",
      "to_email": "bob@example.com",
      "from_email": "alice@gmail.com",
      "subject": "Hello Bob",
      "template_id": null,
      "provider_message_id": "<msg-id@gmail>",
      "status": "sent",
      "sent_at": "2026-06-02T14:05:00.000Z",
      "retry_count": 0,
      "metadata": {},
      "created_at": "2026-06-02T14:02:50.000Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

---

### GET /api/emails/:id

Get a single email log by ID.

**Path parameter**: `id` — email log UUID

**Response** `200 OK`:

```json
{
  "success": true,
  "email": { ... }
}
```

The `email` object has the same shape as items in the list response above.

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Email log not found or not owned by workspace |

---

### Email Status Values

| Status | Description |
|---|---|
| `queued` | Job in Redis queue, not yet processed |
| `sent` | Successfully delivered by provider |
| `failed` | All 3 retries exhausted |
| `bounced` | Provider reported bounce (set externally) |

---
## Templates Service

**Base path**: `/api/templates`  
**Internal port**: `3004`  
**Rate limit**: 100 req/sec, burst 20  
**Auth required**: Yes — `member` role minimum

Templates use **Handlebars** syntax. Variables are double-curly-brace expressions, e.g. `{{name}}`. Templates are versioned — every `PUT` snapshots the current version before applying changes.

---

### POST /api/templates/

Create a new email template.

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Template display name |
| `subject` | string | Yes | Email subject line (Handlebars supported) |
| `html` | string | Yes | HTML body (Handlebars supported) |
| `variables` | string[] | No | Declared variable names (documentation only) |
| `validation_rules` | object | No | Enforcement rules applied at send time (see below) |

**`validation_rules` structure**:

```json
{
  "required": ["name", "company"],
  "maxLength": {
    "name": 100,
    "company": 200
  },
  "pattern": {
    "email": "^[^@]+@[^@]+$"
  }
}
```

| Rule key | Type | Description |
|---|---|---|
| `required` | string[] | Variables that must be present and non-empty |
| `maxLength` | `{ [variable]: number }` | Max string length per variable |
| `pattern` | `{ [variable]: string }` | Regex pattern each variable must match |

**Example request**:

```json
{
  "name": "Welcome Email",
  "subject": "Welcome to {{company}}, {{name}}!",
  "html": "<h1>Hi {{name}}</h1><p>Thanks for joining {{company}}.</p>",
  "variables": ["name", "company"],
  "validation_rules": {
    "required": ["name", "company"],
    "maxLength": { "name": 100 }
  }
}
```

**Response** `201 Created`:

```json
{
  "success": true,
  "template": {
    "template_id": "uuid",
    "workspace_id": "uuid",
    "name": "Welcome Email",
    "subject": "Welcome to {{company}}, {{name}}!",
    "html": "<h1>Hi {{name}}</h1>...",
    "variables": ["name", "company"],
    "validation_rules": { "required": ["name", "company"], "maxLength": { "name": 100 } },
    "created_by": "uuid",
    "version": 1,
    "created_at": "2026-06-02T14:02:50.000Z",
    "updated_at": "2026-06-02T14:02:50.000Z"
  }
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `name`, `subject`, or `html` missing |

---

### GET /api/templates/

List all templates for the workspace, newest first.

**Response** `200 OK`:

```json
{
  "success": true,
  "templates": [ { ... } ]
}
```

Each item has the same shape as the create response `template` object.

---

### PUT /api/templates/:id

Update a template. Before applying changes, the current version is **automatically snapshotted** to `email_template_versions`. The `version` counter increments by 1.

**Path parameter**: `id` — template UUID

**Request body** (all fields optional — only provided fields are updated):

| Field | Type | Description |
|---|---|---|
| `name` | string | New display name |
| `subject` | string | New subject |
| `html` | string | New HTML body |
| `variables` | string[] | Updated variable list |
| `validation_rules` | object | Updated validation rules |

**Response** `200 OK`:

```json
{
  "success": true,
  "template": { ... }
}
```

The returned template has an incremented `version` number.

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Template not found or not owned by workspace |

---

### GET /api/templates/:id/versions

List version history for a template.

**Path parameter**: `id` — template UUID

**Query parameters**:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | number | 1 | Page number |
| `limit` | number | 20 | Items per page |

**Response** `200 OK`:

```json
{
  "success": true,
  "versions": [
    {
      "version_id": "uuid",
      "template_id": "uuid",
      "version": 2,
      "name": "Welcome Email",
      "subject": "Welcome {{name}}!",
      "html": "...",
      "variables": ["name"],
      "validation_rules": {},
      "snapshotted_by": "uuid",
      "snapshotted_at": "2026-06-02T14:10:00.000Z"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 20
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Template not found or not owned by workspace |

---

### POST /api/templates/:id/rollback

Roll back a template to a specific version. The current state is snapshotted before rollback, and the `version` counter increments (rollback is a forward operation, not destructive).

**Path parameter**: `id` — template UUID

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | number | Yes | Target version number to restore |

**Example request**:

```json
{ "version": 2 }
```

**Response** `200 OK`:

```json
{
  "success": true,
  "template": { ... }
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `version` field missing |
| `NOT_FOUND` | Template or target version not found |

---

### DELETE /api/templates/:id

Permanently delete a template. This is a hard delete — the record is removed.

**Path parameter**: `id` — template UUID

**Response** `200 OK`:

```json
{ "success": true }
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Template not found or not owned by workspace |

---
## Webhooks Service

**Base path**: `/api/webhooks`  
**Internal port**: `3008`  
**Rate limit**: 100 req/sec, burst 20  
**Auth required**: Yes — `owner` role required on all endpoints

The webhooks service subscribes to the Redis channel `webhook:events`. When the emails service publishes an event, the dispatcher finds all matching active webhooks for that workspace, creates a delivery record, and attempts HTTP delivery. Failed deliveries are retried with **exponential backoff** (max 5 attempts).

---

### POST /api/webhooks/

Create a new webhook endpoint.

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string | Yes | HTTPS endpoint to deliver events to |
| `events` | string[] | Yes | Event types to subscribe to (see below) |
| `secret` | string | Yes | Signing secret for HMAC verification |

**Supported event types**:

| Event | Trigger |
|---|---|
| `email.sent` | Email successfully delivered by provider |
| `email.failed` | Email exhausted all retries |
| `email.bounced` | Provider reported bounce |

**Example request**:

```json
{
  "url": "https://myapp.example.com/webhooks/mail",
  "events": ["email.sent", "email.failed"],
  "secret": "my-signing-secret-min-32-chars"
}
```

**Response** `201 Created`:

```json
{
  "success": true,
  "webhook_id": "uuid",
  "secret": "my-signing-secret-min-32-chars"
}
```

> **Important**: The `secret` is only returned at creation time. It is stored encrypted (AES-256-GCM) and cannot be retrieved after this response.

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `url`, `events`, or `secret` missing or `events` is empty array |

---

### GET /api/webhooks/

List all webhooks for the workspace. `secret_hash` (encrypted secret) is never returned.

**Response** `200 OK`:

```json
{
  "success": true,
  "webhooks": [
    {
      "webhook_id": "uuid",
      "workspace_id": "uuid",
      "url": "https://myapp.example.com/webhooks/mail",
      "events": ["email.sent", "email.failed"],
      "is_active": true,
      "created_by": "uuid",
      "created_at": "2026-06-02T14:02:50.000Z"
    }
  ]
}
```

---

### PUT /api/webhooks/:id

Update a webhook's URL, events, or active status.

**Path parameter**: `id` — webhook UUID

**Request body** (all fields optional):

| Field | Type | Description |
|---|---|---|
| `url` | string | New delivery URL |
| `events` | string[] | New event subscription list |
| `is_active` | boolean | Enable or disable the webhook |

**Example — disable a webhook**:

```json
{ "is_active": false }
```

**Response** `200 OK`:

```json
{
  "success": true,
  "webhook": {
    "webhook_id": "uuid",
    "workspace_id": "uuid",
    "url": "https://myapp.example.com/webhooks/mail",
    "events": ["email.sent", "email.failed"],
    "is_active": false,
    "created_by": "uuid",
    "created_at": "2026-06-02T14:02:50.000Z"
  }
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Webhook not found or not owned by workspace |

---

### DELETE /api/webhooks/:id

Permanently delete a webhook and all its delivery records.

**Path parameter**: `id` — webhook UUID

**Response** `200 OK`:

```json
{ "success": true }
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Webhook not found or not owned by workspace |

---

### GET /api/webhooks/:id/deliveries

List delivery attempts for a webhook.

**Path parameter**: `id` — webhook UUID

**Query parameters**:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | number | 1 | Page number |
| `limit` | number | 20 | Items per page |

**Response** `200 OK`:

```json
{
  "success": true,
  "deliveries": [
    {
      "delivery_id": "uuid",
      "webhook_id": "uuid",
      "email_id": "uuid",
      "event": "email.sent",
      "payload": { "event": "email.sent", "workspace_id": "...", "email_id": "..." },
      "status": "delivered",
      "attempts": 1,
      "next_retry_at": null,
      "last_error": null,
      "delivered_at": "2026-06-02T14:05:00.000Z",
      "created_at": "2026-06-02T14:04:58.000Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

**Delivery status values**:

| Status | Description |
|---|---|
| `pending` | Not yet attempted or awaiting retry |
| `delivered` | Successfully received by endpoint (2xx response) |
| `failed` | All 5 attempts exhausted |

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Webhook not found or not owned by workspace |

---

### POST /api/webhooks/:id/test

Send a test `email.sent` event delivery to the webhook URL.

**Path parameter**: `id` — webhook UUID

**Response** `200 OK`:

```json
{
  "success": true,
  "delivery_id": "uuid"
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | Webhook not found |

---

### Webhook Payload Format

Every delivery POST to your endpoint sends:

**Headers**:

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |
| `X-Mail-Bridge-Signature` | `sha256=<hmac-hex>` |
| `X-Mail-Bridge-Event` | Event type (e.g. `email.sent`) |

**Body** (example for `email.sent`):

```json
{
  "event": "email.sent",
  "workspace_id": "uuid",
  "email_id": "uuid",
  "to_email": "bob@example.com",
  "subject": "Hello Bob",
  "sent_at": "2026-06-02T14:05:00.000Z",
  "provider_message_id": "<msg-id@gmail>"
}
```

### Verifying the Signature

Compute `HMAC-SHA256` of the raw request body using your webhook secret and compare to the `X-Mail-Bridge-Signature` header:

```javascript
const crypto = require('crypto');

function verifySignature(rawBody, secret, signatureHeader) {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(rawBody)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(signatureHeader)
  );
}
```

### Retry Schedule

On delivery failure, retries follow exponential backoff:

| Attempt | Delay before retry |
|---|---|
| 1 | 60 seconds |
| 2 | 120 seconds |
| 3 | 240 seconds |
| 4 | 480 seconds |
| 5 (final) | No retry — status set to `failed` |

> Formula: `30 * 2^attempt` seconds. The retry loop polls every **30 seconds**.

---
## Admin Service

**Base path**: `/api/admin`  
**Internal port**: `3005`  
**Rate limit**: 100 req/sec, burst 10  
**Auth required**: Yes — `owner` role required on all endpoints

Manages users within the authenticated workspace.

---

### GET /api/admin/users

List all active (non-deleted) users in the workspace.

**Response** `200 OK`:

```json
{
  "success": true,
  "users": [
    {
      "user_id": "uuid",
      "email": "alice@example.com",
      "workspace_id": "uuid",
      "role": "owner",
      "created_at": "2026-06-02T14:02:50.000Z",
      "updated_at": "2026-06-02T14:02:50.000Z"
    }
  ]
}
```

> `password_hash` is never returned.

---

### POST /api/admin/users

Invite a new user to the workspace. The user is created with `password_hash = 'INVITE_PENDING'` — they must set a password through a separate flow.

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | Email address of the user to invite |
| `role` | string | Yes | `owner` or `member` |

**Example request**:

```json
{
  "email": "bob@example.com",
  "role": "member"
}
```

**Response** `201 Created`:

```json
{
  "success": true,
  "user": {
    "user_id": "uuid",
    "email": "bob@example.com",
    "workspace_id": "uuid",
    "role": "member",
    "created_at": "2026-06-02T14:02:50.000Z",
    "updated_at": "2026-06-02T14:02:50.000Z"
  }
}
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `email` or `role` missing |
| `USER_EXISTS` | Email already registered in the system |

---

### PUT /api/admin/users/:id/role

Change the role of a workspace member.

**Path parameter**: `id` — user UUID

**Request body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | string | Yes | `owner` or `member` |

**Example request**:

```json
{ "role": "owner" }
```

**Response** `200 OK`:

```json
{ "success": true }
```

**Error cases**:

| Code | Trigger |
|---|---|
| `INVALID_PAYLOAD` | `role` missing |
| `NOT_FOUND` | User not found or not in workspace |

---

### DELETE /api/admin/users/:id

Soft-delete a user from the workspace (sets `deleted_at`). The user record is retained.

**Path parameter**: `id` — user UUID

**Response** `200 OK`:

```json
{ "success": true }
```

**Error cases**:

| Code | Trigger |
|---|---|
| `NOT_FOUND` | User not found or already deleted |

---
## Health Service

**Base path**: `/health`  
**Internal port**: `3006`  
**Rate limit**: No rate limiting applied (passthrough)  
**Auth required**: No

---

### GET /health

Basic liveness check. Always returns 200 if the service process is running.

**Response** `200 OK`:

```json
{
  "status": "ok",
  "version": "2.0.0",
  "timestamp": "2026-06-02T14:02:50.000Z"
}
```

---

### GET /health/ready

Readiness check. Verifies database and Redis connectivity. Returns 503 if either dependency is down.

**Response** `200 OK` (healthy):

```json
{
  "status": "ready",
  "db": "ok",
  "redis": "ok"
}
```

**Response** `503 Service Unavailable` (unhealthy):

```json
{
  "status": "not_ready",
  "db": "down",
  "redis": "ok"
}
```

| Field | Values | Meaning |
|---|---|---|
| `status` | `ready` / `not_ready` | Overall readiness |
| `db` | `ok` / `down` | PostgreSQL `SELECT 1` result |
| `redis` | `ok` / `down` | Redis `PING` result |

---

## Dashboard Service

**Base path**: `/` (direct access, port `3007`)  
**Internal port**: `3007`  
**Auth required**: Yes (Bearer token)  
**No gateway route** — access directly in development

### GET /

Returns a server-rendered HTML status dashboard. Shows:

- Workspace name and tier
- Active credential count
- Emails sent today (since UTC midnight)
- Last 10 emails (to, subject, status, timestamp)

**Response** `200 OK`: HTML page

This endpoint is intended for internal operational monitoring. It is not part of the public API surface and has no JSON response.

---
## Webhook Event Delivery

This section describes the internal event flow between services — not a public API endpoint.

### Flow

1. **emails service** finishes processing a job (success or permanent failure).
2. It calls `redis.publish('webhook:events', JSON.stringify(payload))`.
3. **webhooks service** has a subscriber listening on `webhook:events`.
4. On receiving a message, the dispatcher queries all active webhooks for the workspace that subscribe to the event type.
5. For each matching webhook: a `webhook_deliveries` record is inserted and `attemptDelivery()` is called immediately.
6. If delivery fails, `next_retry_at` is set using exponential backoff.
7. A **retry loop** polls every 30 seconds for pending deliveries past `next_retry_at` using `SELECT FOR UPDATE SKIP LOCKED` (multi-instance safe).

### Redis Queue

The email queue uses a Redis list at key `mail:queue`.

| Operation | Redis command | Description |
|---|---|---|
| Enqueue | `LPUSH mail:queue <job>` | Push job to head of list |
| Dequeue | `BRPOP mail:queue 5` | Blocking pop from tail (FIFO), 5s timeout |

**Email job payload** (internal, stored as JSON string):

```json
{
  "jobId": "uuid",
  "emailLogId": "uuid",
  "credentialId": "uuid",
  "workspaceId": "uuid",
  "to": "bob@example.com",
  "from": "alice@gmail.com",
  "subject": "Hello",
  "html": "<p>Hi</p>",
  "attachments": []
}
```

### Token Blocklist (Redis)

Logged-out tokens are stored as:

```
SET blocklist:<token> "1" EX <remaining_ttl_seconds>
```

The `authenticate` middleware checks this key on every authenticated request.

---

## Data Models

### Workspace

```typescript
{
  workspace_id: string   // UUID
  name: string
  tier: "free" | "pro" | "enterprise"
  settings: object       // JSONB, default {}
  created_at: string     // ISO 8601
}
```

### User

```typescript
{
  user_id: string        // UUID
  email: string
  workspace_id: string   // UUID
  role: "owner" | "member"
  created_at: string
  updated_at: string
  deleted_at: string | null
}
```

> `password_hash` is never returned in API responses.

### Credential

```typescript
{
  credential_id: string     // UUID
  workspace_id: string      // UUID
  provider_type: "gmail" | "outlook" | "smtp"
  from_email: string
  is_active: boolean
  last_used_at: string | null
  metadata: object
  created_at: string
  encryption_key_id: string
}
```

> `encrypted_value` is never returned in API responses.

### EmailTemplate

```typescript
{
  template_id: string
  workspace_id: string
  name: string
  subject: string           // Handlebars syntax
  html: string              // Handlebars syntax
  variables: string[]       // Declared variable names
  validation_rules: {
    required?: string[]
    maxLength?: { [variable: string]: number }
    pattern?: { [variable: string]: string }
  }
  created_by: string | null // user_id
  version: number           // starts at 1, increments on each PUT
  created_at: string
  updated_at: string
}
```

### EmailTemplateVersion

```typescript
{
  version_id: string
  template_id: string
  version: number
  name: string
  subject: string
  html: string
  variables: string[]
  validation_rules: object
  snapshotted_by: string | null
  snapshotted_at: string
}
```

### EmailLog

```typescript
{
  email_id: string
  workspace_id: string
  credential_id: string | null
  to_email: string
  from_email: string
  subject: string
  template_id: string | null
  provider_message_id: string | null
  status: "queued" | "sent" | "failed" | "bounced"
  sent_at: string | null
  retry_count: number        // max 3
  metadata: object
  created_at: string
}
```

### ScheduledEmail

```typescript
{
  scheduled_id: string
  workspace_id: string
  credential_id: string
  to_email: string
  subject: string
  html: string
  variables: object
  template_id: string | null
  scheduled_at: string       // ISO 8601 UTC
  status: "pending" | "queued" | "cancelled"
  created_by: string | null
  created_at: string
}
```

### Webhook

```typescript
{
  webhook_id: string
  workspace_id: string
  url: string
  events: ("email.sent" | "email.failed" | "email.bounced")[]
  is_active: boolean
  created_by: string | null
  created_at: string
}
```

### WebhookDelivery

```typescript
{
  delivery_id: string
  webhook_id: string
  email_id: string | null
  event: "email.sent" | "email.failed" | "email.bounced"
  payload: object
  status: "pending" | "delivered" | "failed"
  attempts: number           // max 5
  next_retry_at: string | null
  last_error: string | null
  delivered_at: string | null
  created_at: string
}
```

---

## Internal Architecture

### Service Communication

Services communicate through **shared PostgreSQL and Redis only** — no direct HTTP calls between services. This is intentional for fault isolation.

| Channel | Used for |
|---|---|
| PostgreSQL | Persistent data (all tables) |
| Redis list `mail:queue` | Email job queue (FIFO) |
| Redis pubsub `webhook:events` | Event fan-out from emails → webhooks |
| Redis keys `blocklist:*` | Logout token blocklist |

### Request Tracing

Each request gets an `id` attached by the exception-handling middleware. It appears in error logs as `req_id`. The gateway also injects `X-Device-Fingerprint` for client identification.

### Encryption

- Credentials (OAuth tokens, SMTP passwords) are encrypted with **AES-256-GCM** using `CREDENTIAL_MASTER_KEY`.
- Each credential has a unique `encryption_key_id` (random UUID) used as part of the encryption context.
- Webhook secrets are encrypted with the same scheme, stored as `keyId:encryptedValue`.

### JWT Security

- Signed with `JWT_SECRET` using HS256.
- Each token has a unique `jti` (JWT ID) — a random UUID.
- Tokens are blocklisted in Redis on logout.
- Expiry defaults to 24 hours (configurable via `JWT_EXPIRES_IN`).

---
## How-To Guide

### 1. Register and get a token

```bash
curl -X POST http://localhost:3009/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123",
    "workspace_name": "Acme Corp"
  }'
```

Save the returned `token` — you'll need it for all subsequent requests.

---

### 2. Add a sending credential

**SMTP example**:

```bash
curl -X POST http://localhost:3009/api/credentials/smtp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "from_email": "noreply@acme.com",
    "host": "smtp.sendgrid.net",
    "port": 587,
    "secure": false,
    "user": "apikey",
    "pass": "SG.xxxxx"
  }'
```

Save the returned `credential_id`.

**Gmail OAuth flow**:

1. `GET /api/credentials/gmail/connect` — get the Google consent URL
2. Open the URL in a browser and authorize
3. Google redirects to `/api/credentials/gmail/callback?code=...&state=<workspace_id>`
4. The credential is stored automatically

---

### 3. Send a single email

```bash
curl -X POST http://localhost:3009/api/emails/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "credential_id": "<credential_id>",
    "to_email": "bob@example.com",
    "subject": "Hello Bob",
    "html": "<p>Welcome!</p>"
  }'
```

---

### 4. Create a template and send with variables

**Create template**:

```bash
curl -X POST http://localhost:3009/api/templates \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Onboarding",
    "subject": "Welcome to {{company}}, {{name}}!",
    "html": "<h1>Hi {{name}}</h1><p>Thanks for joining {{company}}.</p>",
    "variables": ["name", "company"],
    "validation_rules": {
      "required": ["name", "company"]
    }
  }'
```

**Send using template**:

```bash
curl -X POST http://localhost:3009/api/emails/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "credential_id": "<credential_id>",
    "to_email": "bob@example.com",
    "template_id": "<template_id>",
    "variables": {
      "name": "Bob",
      "company": "Acme Corp"
    }
  }'
```

---

### 5. Send a batch

```bash
curl -X POST http://localhost:3009/api/emails/batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "emails": [
      {
        "credential_id": "<credential_id>",
        "to_email": "alice@example.com",
        "subject": "Hello Alice",
        "html": "<p>Hi Alice!</p>"
      },
      {
        "credential_id": "<credential_id>",
        "to_email": "bob@example.com",
        "subject": "Hello Bob",
        "html": "<p>Hi Bob!</p>"
      }
    ]
  }'
```

---

### 6. Schedule a future email

```bash
curl -X POST http://localhost:3009/api/emails/schedule \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "credential_id": "<credential_id>",
    "to_email": "bob@example.com",
    "subject": "Scheduled reminder",
    "html": "<p>This is your reminder.</p>",
    "scheduled_at": "2026-06-15T09:00:00.000Z"
  }'
```

---

### 7. Register a webhook

```bash
curl -X POST http://localhost:3009/api/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "url": "https://myapp.example.com/hooks/mail",
    "events": ["email.sent", "email.failed"],
    "secret": "my-very-long-signing-secret-here"
  }'
```

> Store the returned `secret` securely — it cannot be retrieved later.

---

### 8. Verify a webhook delivery (Node.js)

```javascript
const crypto = require('crypto');
const express = require('express');

const app = express();
app.use(express.raw({ type: 'application/json' }));

app.post('/hooks/mail', (req, res) => {
  const signature = req.headers['x-mail-bridge-signature'];
  const secret = process.env.WEBHOOK_SECRET;

  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(req.body)
    .digest('hex');

  if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature))) {
    return res.status(401).send('Invalid signature');
  }

  const event = JSON.parse(req.body);
  console.log('Received event:', event.event, 'for email:', event.email_id);

  res.status(200).send('OK');
});
```

---

### 9. Upgrade to Pro

```bash
curl -X POST http://localhost:3009/auth/upgrade \
  -H "Authorization: Bearer <token>"
```

Replace the stored token with the new one returned in the response.

---

### 10. Invite a team member

```bash
curl -X POST http://localhost:3009/api/admin/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "email": "dave@acme.com",
    "role": "member"
  }'
```

---

### 11. Check health

```bash
# Liveness
curl http://localhost:3009/health

# Readiness (checks DB + Redis)
curl http://localhost:3009/health/ready
```

---

### 12. Paginating results

All list endpoints support `page` and `limit` query parameters:

```bash
# Page 2, 50 items per page
curl "http://localhost:3009/api/emails?page=2&limit=50" \
  -H "Authorization: Bearer <token>"
```

Default values: `page=1`, `limit=20`.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection string |
| `JWT_SECRET` | Yes | — | Min 32 chars, signs all JWTs |
| `JWT_EXPIRES_IN` | No | `24h` | Token lifetime (e.g. `1h`, `7d`) |
| `CREDENTIAL_MASTER_KEY` | Yes | — | 64 hex chars, AES-256-GCM master key |
| `GMAIL_CLIENT_ID` | Gmail only | — | Google OAuth client ID |
| `GMAIL_CLIENT_SECRET` | Gmail only | — | Google OAuth client secret |
| `GMAIL_REDIRECT_URI` | Gmail only | — | OAuth callback URL |
| `OUTLOOK_CLIENT_ID` | Outlook only | — | Azure AD app client ID |
| `OUTLOOK_CLIENT_SECRET` | Outlook only | — | Azure AD app client secret |
| `OUTLOOK_TENANT_ID` | Outlook only | `common` | Azure AD tenant ID |
| `BATCH_MAX_SIZE` | No | `100` | Max emails per batch request |
| `LOG_LEVEL` | No | `info` | `debug`/`info`/`warn`/`error` |
| `PORT` | No | service-specific | Override service listen port |

---

*Mail-Bridge API Documentation — Generated 2026-06-02*
