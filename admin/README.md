# JobHunter Admin Console

Next.js 15 frontend for the JobHunter Admin API. Provides scraper control, live log streaming, and task monitoring for administrators.

> **Port:** 5001 (host) → 3001 (container) | **Phase:** 1 | **Status:** Complete

---

## Quick Start

```bash
cd admin/
npm install
cp .env.local.example .env.local   # if present, else set NEXT_PUBLIC_ADMIN_API_URL manually
npm run dev
# URL: https://admin.myjobhunter.in (Docker / Prod via Nginx)
```

---

## Stack

| Tool | Role |
|---|---|
| Next.js 15 (App Router) | Routing, middleware, SSR |
| TypeScript (strict) | Type safety |
| Vanilla CSS | Styling |
| Zustand | Auth state store |
| Axios | HTTP client with JWT interceptors and refresh queue |
| Jest + Testing Library | Unit tests |
| Geist | Typography |

---

## Pages

| Route | Description | Auth |
|---|---|---|
| `/login` | Admin login form | Public |
| `/dashboard` | Redirects to `/dashboard/scraper` | Protected |
| `/dashboard/scraper` | Scraper trigger form, status, live log viewer | Protected |

---

## Directory Structure

```
admin/
├── app/
│   ├── layout.tsx               # Root layout — fonts, metadata
│   ├── page.tsx                 # Redirects to /dashboard/scraper
│   ├── (auth)/
│   │   ├── layout.tsx           # Centered layout for login
│   │   └── login/page.tsx       # Login form with loading + error state
│   └── (protected)/
│       ├── layout.tsx           # Sidebar + logout button
│       ├── dashboard/page.tsx   # Redirects to /dashboard/scraper
│       └── dashboard/scraper/page.tsx  # Scraper control + live logs
├── features/auth/
│   └── authStore.ts             # Zustand store (token, user, login, logout)
├── lib/
│   └── api.ts                   # Axios instance — request interceptor (token injection)
│                                #   + response interceptor (refresh queue + retry)
├── middleware.ts                # Checks admin_refresh cookie — redirects to /login if absent
├── next.config.ts               # /api/* rewrites to admin-api:8003, CSP headers
├── __tests__/
│   ├── authStore.test.ts        # 3 unit tests for Zustand store
│   └── LoginPage.test.tsx       # 3 tests — render, submit, error handling
├── jest.config.ts
├── jest.setup.ts
├── Dockerfile                   # Multi-stage: deps → builder → runner (Node 20, standalone)
└── package.json
```

---

## Architecture

```
Browser :5001
  └─ Next.js middleware.ts  →  checks admin_refresh cookie
        ├─ missing  →  redirect /login
        └─ present  →  allow through to (protected) routes
              └─ /api/* rewrites  →  admin-api:8003 (server-side)
                    └─ lib/api.ts interceptors  →  inject Bearer token, handle refresh
```

---

## Configuration

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_ADMIN_API_URL` | Admin API base URL — baked in at build time. Set to `http://admin-api:8003` in Docker. |

The `next.config.ts` rewrites `/api/*` to the admin-api service at build-time, so the browser always calls `/api/*` on the same origin.

---

## Running Tests

```bash
npm test              # run jest
npm run typecheck     # tsc --noEmit
npm run lint          # next lint
```

---

## Docker

```bash
docker compose up -d --build admin
# Accessible at https://admin.myjobhunter.in
```

The Dockerfile uses a multi-stage build (`deps → builder → runner`) with Next.js standalone output. The final image runs as a non-root `nextjs` user.
