# JobHunter Scraper Engine

Phase 1 — scrapes, cleans, normalises, and deduplicates job listings from Indeed India and Naukri.com.
Also provides **Module 1: Company Discovery** (bootstrap + keyword-driven search + enrichment pipeline)
and **Module 2: Career Page Job Scraper** (ATS API + extraction cascade).

## Quick Start

```bash
# 1. Setup
bash scripts/setup_dev_env.sh        # creates .venv, installs deps, installs Chromium
source .venv/bin/activate

# 2. Run dev mode (Naukri pipeline by default)
python -m dev_mode.dev_runner

# 3. Run tests
bash scripts/run_tests.sh

# 4. Run the Redis worker (requires running Redis)
python -m scraper_worker.worker
```

## Install as package

```bash
pip install -e ".[dev]"
```

## Docker

```bash
# From the project root
docker compose up -d --build scraper
# Worker listens on redis:6379 for tasks on the scraper:tasks queue
```

## Architecture

```
Scheduler -> Worker -> Scraper -> Extraction -> Cleaning -> Normalization -> Deduplication -> Output
```

### Scraper Channels

| Channel | Description | Status |
|---|---|---|
| Naukri | JSON API — active job listings | Active |
| Indeed | Playwright + stealth | Active |
| LinkedIn | Playwright stub | Phase 1 |
| Company Discovery | Bootstrap + keyword search -> company enrichment | In Progress |
| Career Pages | ATS API + extraction cascade from company career pages | In Progress |

## Sources (Job Boards)

| Source   | Method      | Status     |
|----------|-------------|------------|
| Naukri   | JSON API    | Active     |
| Indeed   | Playwright  | Active     |
| LinkedIn | Playwright  | Phase 1    |

## Module 1 — Company Discovery (`scraper/scraper/sources/company_discovery/`)

Builds and continuously expands the `companies` database. Operates in two modes:

**Bootstrap Mode** — Imports from static public sources (no admin input required):
- Open-source company datasets (GitHub CSV lists, GLEIF public data)
- Government registries (MCA21 via data.gov.in, Startup India portal API)
- VC/accelerator portfolio pages (Sequoia, Accel, Blume, 100X.VC, IIT/IIM incubators, etc.)
- GitHub organization discovery (public Search API, extracts `blog` field)
- Public directories (Zauba Corp, NASSCOM member directory, CII member directory)

**Discovery Mode** — Admin-initiated. Takes role, location, experience, salary inputs.
Runs DuckDuckGo headless search (Bing fallback) with multiple query variants.
Extracts company domains from results, discards known job boards.

**Enrichment Pipeline** — Every domain passes through in order:
1. `robots.txt` compliance check — non-negotiable, halts on block
2. Career page discovery (URL pattern probe → homepage link parse → sitemap)
3. Email extraction (`mailto:` links, regex, schema.org ContactPoint)
4. Email classification (deterministic: HR keywords vs general, free webmail flagged)
5. ATS detection (Greenhouse, Lever, Ashby, Workday, SmartRecruiters, and 6 others)
6. Company metadata extraction (name, industry, location from structured data)

**Deduplication** — 5-layer strategy: apex domain normalization (primary key),
composite fingerprint (MD5 of normalized name + domain), email domain cross-check,
subdomain-to-parent linking, multi-domain same-company linking.

## Module 2 — Career Page Job Scraper (`scraper/scraper/sources/career_page/`)

Extracts active job listings from every enriched company's career page.

**ATS Routing** — Greenhouse, Lever, Ashby use free public JSON APIs (no auth).
Workday, SmartRecruiters, BambooHR, Teamtailor, Recruitee fall back to Playwright.

**Extraction Cascade** (in priority order, first success wins):
1. ATS public API (Greenhouse / Lever / Ashby)
2. JSON-LD `JobPosting` structured data
3. XML sitemap job URL discovery
4. XHR/fetch API reverse engineering (intercepts network calls during page render)
5. Direct HTML parsing (repeating structural patterns)
6. Full Playwright render with internal link extraction (last resort)

**Change Detection** — MD5 content hash of title + description. On re-crawl:
unchanged jobs update `last_seen_at` only; changed jobs re-parse all fields.
Missing jobs across two consecutive crawls are marked `status = closed`.

## Output

Jobs from all channels are written to PostgreSQL.
Company records go to the `companies` table.
Career page jobs go to the `career_jobs` table.
Naukri/Indeed jobs go to the `jobs` table.

If `OUTPUT_FORMATS` is set to `json,csv`, jobs are also written to `output/final/`.

## Configuration

Copy `.env.example` to `.env` and adjust values. All settings have sensible defaults for dev mode.

Key environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `DEV_MODE` | `true` | Enables debug logging |
| `HEADLESS` | `true` | Run browser headless |
| `PAGES_PER_SEARCH` | `5` | Pages scraped per keyword/location |
| `INDEED_RATE_LIMIT` | `1.0` | Requests/sec for Indeed |
| `NAUKRI_RATE_LIMIT` | `0.5` | Requests/sec for Naukri |
| `OUTPUT_FORMATS` | _(empty)_ | Output file formats (e.g. `json,csv`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `PROXY_LIST` | _(empty)_ | Comma-separated proxy URLs |
| `USE_REGISTRY` | `false` | Persist jobs to shared `JobRegistry` |
| `REGISTRY_PATH` | `registries/jobs.json` | Path to the registry JSON file |
| `GITHUB_TOKEN` | _(empty)_ | Optional GitHub PAT for org discovery (increases rate limit from 60 to 5000 req/hr) |

## Redis Worker

The `scraper_worker/worker.py` process listens on the `scraper:tasks` Redis queue using `BLPOP`.
It runs the full scraper pipeline on each task received. New queue keys for company discovery:

| Queue Key | Task |
|---|---|
| `scraper:tasks` | Naukri / Indeed scrape jobs |
| `queue:company_discovery_bootstrap` | Bootstrap source import |
| `queue:company_discovery_search` | Keyword-driven company discovery |
| `queue:career_page_scrape` | Career page job extraction |

```bash
# Requires REDIS_URL set in .env
python -m scraper_worker.worker
```

## Running specific scrapers

```python
from dev_mode.dev_runner import DevModeRunner
import asyncio

runner = DevModeRunner()
asyncio.run(runner.run_naukri_scraper(keywords=["Python Developer"], locations=["Bangalore"]))
asyncio.run(runner.run_indeed_scraper(keywords=["Data Analyst"], locations=["Mumbai"]))
asyncio.run(runner.run_full_pipeline("naukri", keywords=["Django"], locations=["Hyderabad"]))
```

## Code quality

```bash
.venv/bin/black --check scraper/
.venv/bin/flake8 scraper/
.venv/bin/pytest tests/ -v
```

## Compliance

- `robots.txt` is checked before every request to a new domain — non-negotiable
- Rate limits enforced via token-bucket `RateLimiter` (per-domain)
- Google excluded (TOS); DuckDuckGo HTML endpoint primary, Bing HTML fallback
- LinkedIn excluded (TOS) — permanent until official API partnership
- User-Agent header identifies the scraper with a contact reference
- Free webmail HR contacts are stored but flagged `email_trust: low_trust`
