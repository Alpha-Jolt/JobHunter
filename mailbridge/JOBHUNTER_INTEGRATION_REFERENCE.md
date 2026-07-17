# Mail-Bridge × JobHunter — Integration Reference (Mail-Bridge Side)

**Version**: 1.0.0  
**Date**: 17/07/2026  
**Scope**: Mail-Bridge API endpoints consumed by JobHunter. No changes to this codebase.

---

## Overview

JobHunter integrates as a **headless API client** using an API key (`sk_...`). All email delivery is offloaded to Mail-Bridge. This document records what JobHunter uses from Mail-Bridge and the one-time setup steps a developer must perform.

---

## Endpoints Used by JobHunter

| Operation | Method | Path | Scope Required |
|---|---|---|---|
| Send single email | POST | `/api/emails/send` | `send` |
| Send batch (up to 100) | POST | `/api/emails/batch` | `send` |
| Schedule future email | POST | `/api/emails/schedule` | `send` |
| Cancel scheduled email | DELETE | `/api/emails/schedule/:id` | `send` |
| Get email delivery status | GET | `/api/emails/:id` | `read` |
| List Gmail credentials | GET | `/api/credentials/` | `credentials` |
| Register Gmail watch | POST | `/api/credentials/:id/watch` | `credentials` |
| Create email template | POST | `/api/templates` | `templates` |
| Register delivery webhook | POST | `/api/webhooks` | owner JWT |
| Update webhook events | PUT | `/api/webhooks/:id` | owner JWT |
| Test webhook delivery | POST | `/api/webhooks/:id/test` | owner JWT |

---

## One-Time Developer Setup (Checklist)

### Step 1 — Create API Key

Console: `http://localhost:3010` → Settings → API Keys

Required scopes: `send`, `read`, `templates`

Copy the `sk_...` value. Store in `MAILBRIDGE_API_KEY` in JobHunter `.env`.

---

### Step 2 — Get Credential ID

```bash
curl https://bridge.myjobhunter.in/api/credentials/ \
  -H "Authorization: Bearer sk_..."
```

Find `myjobhunter.business@gmail.com`. Copy `id` → `MAILBRIDGE_CREDENTIAL_ID` in JobHunter `.env`.

---

### Step 3 — Register Gmail Watch

```bash
curl -X POST https://bridge.myjobhunter.in/api/credentials/<CREDENTIAL_ID>/watch \
  -H "Authorization: Bearer sk_..."
```

Renew this every 6 days (JobHunter handles this automatically via background task).

---

### Step 4 — Create Email Templates

Run these once to register templates in Mail-Bridge. Copy the returned UUIDs into `orchestration/config/mailbridge_templates.py` in JobHunter.

#### `jh_job_application`

```bash
curl -X POST https://bridge.myjobhunter.in/api/templates \
  -H "Authorization: Bearer sk_..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jh_job_application",
    "subject": "Application for {{job_title}} at {{company_name}}",
    "html": "<p>Dear Hiring Manager,</p><p>I am writing to apply for the <strong>{{job_title}}</strong> position at <strong>{{company_name}}</strong>. Please find my resume and cover letter attached.</p><p>Best regards,<br>{{candidate_name}}</p>",
    "variables": ["candidate_name", "job_title", "company_name"],
    "validation_rules": { "required": ["candidate_name", "job_title", "company_name"] }
  }'
```

#### `jh_follow_up_reminder`

```bash
curl -X POST https://bridge.myjobhunter.in/api/templates \
  -H "Authorization: Bearer sk_..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jh_follow_up_reminder",
    "subject": "Following up on my application for {{job_title}}",
    "html": "<p>Dear Hiring Team,</p><p>I wanted to follow up on my application for <strong>{{job_title}}</strong> submitted {{days_since}} days ago. I remain very interested in this opportunity.</p><p>Best regards,<br>{{candidate_name}}</p>",
    "variables": ["candidate_name", "job_title", "days_since"],
    "validation_rules": { "required": ["candidate_name", "job_title", "days_since"] }
  }'
```

#### `jh_application_confirmation`

```bash
curl -X POST https://bridge.myjobhunter.in/api/templates \
  -H "Authorization: Bearer sk_..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jh_application_confirmation",
    "subject": "Your application for {{job_title}} at {{company}} has been submitted",
    "html": "<p>Hi {{candidate_name}},</p><p>Your application for <strong>{{job_title}}</strong> at <strong>{{company}}</strong> has been sent. We will update you when we hear back.</p><p>The JobHunter Team</p>",
    "variables": ["candidate_name", "job_title", "company"],
    "validation_rules": { "required": ["candidate_name", "job_title", "company"] }
  }'
```

---

### Step 5 — Register Webhook

```bash
curl -X POST https://bridge.myjobhunter.in/api/webhooks \
  -H "Authorization: Bearer <owner-jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.myjobhunter.in/api/webhooks/mailbridge",
    "events": ["email.sent", "email.failed", "email.received"],
    "secret": "<MAILBRIDGE_WEBHOOK_SECRET — min 32 chars>"
  }'
```

Copy returned `id` → `MAILBRIDGE_WEBHOOK_ID` in JobHunter `.env`.  
The `secret` cannot be retrieved again — store it immediately.

---

## Webhook Payload Reference

### `email.sent`

```json
{
  "event": "email.sent",
  "workspace_id": "uuid",
  "email_id": "uuid",
  "to_email": "hr@company.com",
  "subject": "Application for Software Engineer at Acme",
  "sent_at": "2026-07-17T10:00:00.000Z",
  "provider_message_id": "<msg-id@gmail>"
}
```

### `email.failed`

```json
{
  "event": "email.failed",
  "workspace_id": "uuid",
  "email_id": "uuid",
  "to_email": "hr@company.com",
  "error": "Gmail delivery failed: 550 5.1.1 unknown user"
}
```

### `email.received`

```json
{
  "event": "email.received",
  "workspace_id": "uuid",
  "payload": {
    "from": "hr@company.com",
    "subject": "Re: Your application",
    "received_at": "2026-07-17T12:00:00.000Z",
    "snippet": "Thank you for applying..."
  }
}
```

---

## Signature Verification

Every webhook POST from Mail-Bridge includes:

```
X-Mail-Bridge-Signature: sha256=<hex-digest>
```

JobHunter verifies using:

```python
expected = "sha256=" + hmac.new(
    MAILBRIDGE_WEBHOOK_SECRET.encode(),
    raw_body,
    hashlib.sha256,
).hexdigest()
assert hmac.compare_digest(expected, signature_header)
```

Always use `hmac.compare_digest` — never `==`.

---

## API Key Scopes Required

| Scope | Used for |
|---|---|
| `send` | `POST /api/emails/send`, `/batch`, `/schedule`, `DELETE /api/emails/schedule/:id` |
| `read` | `GET /api/emails/:id` |
| `templates` | `POST /api/templates`, `GET /api/templates` |
| `credentials` | `GET /api/credentials/`, `POST /api/credentials/:id/watch` |

Webhook registration requires a **Bearer JWT** (owner role), not an API key.

---

## Rate Limits (Mail-Bridge Nginx)

| Zone | Rate | Burst |
|---|---|---|
| `/api/emails/` | 100 req/s | 50 |
| `/api/templates/` | 100 req/s | 20 |
| `/api/webhooks/` | 100 req/s | 20 |
| `/api/credentials/` | 100 req/s | 20 |

For bulk sends, always use `/api/emails/batch` (up to 100 per call) rather than looping `/api/emails/send`.

---

*No changes are required to the Mail-Bridge codebase for this integration.*
