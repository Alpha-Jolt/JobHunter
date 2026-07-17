# website

## Overview

Next.js 15 public marketing site for Mail-Bridge. Serves the landing page, pricing tiers, and a full documentation system backed by MDX files.

## Key Capabilities

- Static site generation (SSG) — all pages prerendered at build time
- MDX-powered docs with syntax highlighting, slug anchors, and GFM tables
- Dark/light theme via `next-themes`
- Framer Motion hero animation (client-only, `ssr: false`)
- 9 documentation pages covering the full platform

## Architecture Overview

```
website:3011
  /              — Landing page (Hero, Features, HowItWorks, CTA)
  /pricing       — 3-tier pricing cards (Free / Pro / Enterprise)
  /docs          — Redirects to /docs/quickstart
  /docs/[slug]   — MDX doc pages (SSG via generateStaticParams)
```

## Docs Pages

| Slug | Title |
|---|---|
| `quickstart` | Quickstart |
| `authentication` | Authentication |
| `sending-emails` | Sending Emails |
| `templates` | Templates |
| `credentials` | Credentials |
| `webhooks` | Webhooks |
| `api-reference` | API Reference |
| `self-hosting` | Self-hosting |
| `architecture` | Architecture |

## Adding a Doc Page

1. Create `content/docs/<slug>.mdx` with frontmatter:
   ```mdx
   ---
   title: My Page
   description: Short description
   lastUpdated: 2026-05-23
   order: 10
   ---
   ```
2. The sidebar and `generateStaticParams` pick it up automatically — no code changes needed.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `NODE_ENV` | No | `development` / `production` |
| `PORT` | No | Default `3011` |

No backend connection — fully static.

## Quick Start

```bash
cd website
npm install
npm run dev
```

## Dependencies

### Runtime
- `next 15.1.0` — framework
- `react 19.0.0` — UI
- `next-mdx-remote 5.0.0` — MDX rendering (RSC-compatible)
- `gray-matter 4.0.3` — frontmatter parsing
- `rehype-highlight 7.0.0` — code syntax highlighting
- `rehype-slug 6.0.0` — heading anchor IDs
- `remark-gfm 4.0.0` — GitHub Flavored Markdown
- `framer-motion 12.40.0` — hero animation
- `next-themes 0.4.6` — dark/light theme
- `lucide-react 1.16.0` — icons

## Known Limitations

- No search functionality (Fuse.js is installed but not wired — Phase 2)
- No versioned docs
- Pricing page links to `localhost:3010` — update to production URL before deploy
