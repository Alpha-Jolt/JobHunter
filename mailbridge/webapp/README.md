# webapp

## Overview

Next.js 15 management console for Mail-Bridge. Provides an authenticated dashboard for managing credentials, sending emails, creating templates, configuring webhooks, and administering workspace members.

## Key Capabilities

- JWT authentication via httpOnly cookies — no tokens in browser JS
- Server-side JWT decoding — user info never stored in cookies beyond the token
- Full dashboard: emails, templates, credentials, webhooks, admin, settings
- Real-time global email status statistics (Sent, Failed, Queued) visualization
- TanStack Query for server state with per-resource stale times
- Zustand for client auth state
- Dark/light theme via `next-themes`
- Middleware-enforced RBAC — owner-only routes redirect members

## Architecture Overview

```
Browser → webapp:3010
  /api/auth/*     — Next.js API routes (set/clear httpOnly cookie)
  /api/*          — proxied to gateway:3009 server-side
  /(auth)         — login, register (unauthenticated)
  /(dashboard)    — all protected pages (requires mb_token cookie)
```

## Auth Flow

1. User POSTs credentials to `/api/auth/login` (Next.js route)
2. Route calls `gateway:3009/auth/login`, receives JWT
3. JWT stored as `mb_token` httpOnly cookie (`sameSite: strict`, `maxAge: 86400`)
4. All subsequent API calls go through Next.js server — cookie forwarded automatically
5. `middleware.ts` decodes JWT on every request, redirects unauthenticated users
6. `/api/auth/me` decodes JWT server-side and returns user object — no `NEXT_PUBLIC_*` backend URLs
7. `/api/auth/upgrade` POST route calls `gateway:3009/auth/upgrade` to change the workspace tier and returns a new JWT, which is set in the `mb_token` cookie

## Route Reference

| Route | Description | Role |
|---|---|---|
| `/login` | Sign in | — |
| `/register` | Create workspace | — |
| `/` | Dashboard overview | any |
| `/emails` | Email log list | any |
| `/emails/send` | Send single email | any |
| `/emails/batch` | Batch send | any |
| `/emails/schedule` | Scheduled emails | any |
| `/templates` | Template list | any |
| `/templates/new` | Create template | any |
| `/templates/[id]` | Edit template | any |
| `/templates/[id]/versions` | Version history | any |
| `/credentials` | Credential list | owner |
| `/credentials/new` | Add SMTP credential | owner |
| `/webhooks` | Webhook list | owner |
| `/webhooks/new` | Create webhook | owner |
| `/webhooks/[id]/deliveries` | Delivery history | owner |
| `/admin` | Team management | owner |
| `/settings` | Account settings | any |

## Configuration

| Variable | Required | Description |
|---|---|---|
| `API_GATEWAY_URL` | Yes | Internal URL of gateway (server-side only, never `NEXT_PUBLIC_`) |
| `NODE_ENV` | No | `development` / `production` |
| `PORT` | No | Default `3010` |

## Quick Start

```bash
cd webapp
cp .env.local.example .env.local
# Set API_GATEWAY_URL=http://localhost:3009
npm install
npm run dev
```

## Dependencies

### Runtime
- `next 15.1.0` — framework
- `react 19.0.0` — UI
- `@tanstack/react-query 5.62.0` — server state
- `zustand 4.4.7` — client auth state
- `react-hook-form 7.76.1` + `@hookform/resolvers 3.10.0` + `zod 3.22.4` — forms + validation
- `jwt-decode 4.0.0` — server-side JWT decoding in API routes
- `next-themes 0.4.6` — dark/light theme
- `lucide-react 1.16.0` — icons
- `date-fns 3.2.0` — date formatting

## Known Limitations

- No OAuth callback handling in webapp — OAuth redirects go through gateway directly
- No email preview in send form — HTML rendered as-is
- Template preview uses a lightweight inline renderer, not full Handlebars (no partials/helpers)
