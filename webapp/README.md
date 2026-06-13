# JobHunter Webapp

Next.js 15 frontend for the JobHunter platform. Serves as the primary user interface for the full job application automation flow: authentication → job discovery → resume upload → variant generation → approval → application sending.

> **Port:** 3000 | **Phase:** 1 MVP | **Status:** Complete  
> **Stack:** Next.js 15 · TypeScript (strict) · Tailwind 4 · shadcn/ui · Zustand · Axios · Zod · Framer Motion

---

## Quick Start

```bash
cd webapp/
cp .env.example .env.local
# Set NEXT_PUBLIC_API_BASE_URL to your orchestration API (default: http://localhost:8000)

npm install
npm run dev       # Development server → http://localhost:3000
npm run build     # Production build (standalone)
npm run start     # Serve production build
npm run typecheck # TypeScript strict check
npm run lint      # ESLint
```

---

## Docker

```bash
# Build
docker build \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  -t jobhunter-webapp .

# Run
docker run -p 3000:3000 jobhunter-webapp
```

---

## Directory Structure

```
webapp/
├── src/
│   ├── app/                       # Next.js App Router
│   │   ├── (auth)/                # Unauthenticated pages (login, signup)
│   │   └── (protected)/          # JWT-gated pages (dashboard, jobs, resume, variants, applications)
│   ├── features/
│   │   ├── auth/                  # LoginForm, SignupForm, AuthGuard
│   │   ├── jobs/                  # useJobs, JobCard, JobFilters
│   │   ├── resume/                # ResumeUpload (with file security validation)
│   │   ├── variants/              # useVariants, VariantCard (approval flow)
│   │   ├── applications/          # SendApplicationForm, ApplicationHistory
│   │   └── dashboard/             # DashboardMetrics
│   ├── shared/
│   │   ├── api/                   # Axios client, gateway methods, typed errors
│   │   ├── state/                 # Zustand stores (auth, jobs, variants, userProfile, ui)
│   │   ├── components/            # Button, Input, Card, Badge, Skeleton, Toaster
│   │   ├── hooks/                 # useAsync, useForm
│   │   ├── layout/                # Navbar, ThemeToggle, UserMenu
│   │   └── utils/                 # cn, validation (Zod schemas), date helpers
│   ├── lib/
│   │   └── config.ts              # Environment variable access
│   └── middleware.ts              # Refresh-cookie auth guard for all protected routes
├── public/
│   └── manifest.json              # PWA manifest
├── Dockerfile                     # Multi-stage standalone build
├── next.config.ts                 # Standalone output, security headers
└── .env.example
```

---

## Architecture Overview

- **No backend logic in the frontend.** All persistence and business rules stay in the FastAPI Orchestration API (port 8000).
- **API Gateway pattern.** All HTTP calls go through `src/shared/api/gateway.ts` via a single Axios instance with interceptors — never direct fetch in components.
- **Token strategy.** Access token lives in Zustand memory only. Refresh token is an httpOnly cookie set by the backend. On 401, the Axios interceptor calls `/api/auth/refresh` transparently and retries.
- **Variant approval tokens** are stored in `sessionStorage` keyed by `jh_vt_{variant_id}`. They are validated for 3-part HMAC format before storage, cleared immediately after a successful approve call, and wiped on logout.
- **Feature-based folder structure.** Features import only from `@/shared/*`. Cross-feature state coupling is forbidden.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Orchestration API base URL |
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` | Frontend base URL |

---

## Pages & Routes

| Route | Description |
|---|---|
| `/login` | Email + password sign-in |
| `/signup` | Account registration (role: hunter by default) |
| `/dashboard` | Metrics overview + quick actions |
| `/jobs` | Job listing with source filter and search |
| `/resume` | Master resume upload (PDF/DOCX, max 10 MB) |
| `/variants` | Pending variant review, preview, approve, reject |
| `/applications` | Sent applications and status |

---

## Resume Upload Security

Client-side (before upload):
- Extension whitelist (`.pdf`, `.docx` only)
- Magic byte verification (rejects MIME-spoofed files)
- PDF CVE scan: rejects `/JavaScript`, `/OpenAction`, `/Launch`, `/EmbeddedFile`, `/AA`, `/RichMedia`
- DOCX scan: rejects files containing `vbaProject.bin` (VBA macros)
- Filename sanitization (strips path traversal, null bytes, non-safe characters)
- 10 MB size cap

Server-side (`POST /api/resume/upload`):
- JWT required (`get_current_user`)
- Role gate: `hunter` and `admin` only (`require_role`)
- Ownership check: `user_id` must match authenticated user
- All client-side checks repeated server-side
- File uploaded to MinIO at `resumes/{user_id}/{filename}`

---

## Theming

Light/dark/system modes via `next-themes`. Default: system preference.

Brand colours: Orange `#F97316` (primary), Charcoal `#3D3D3D` (neutral). Defined as CSS custom properties in `globals.css` — both modes supported.

---

## Known Limitations (Phase 1)

- Google OAuth button is a placeholder — backend endpoint not yet implemented.
- Variant approval token is lost if the user closes the tab before approving. Regenerating the variant issues a new token.
- Application history shows only today's sent applications (backed by `/api/mail/sent-today`). Full history endpoint is a Phase 2 item.
