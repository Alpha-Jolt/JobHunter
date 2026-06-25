# JobHunter Scraper Engine

Phase 0 MVP — scrapes, cleans, normalises, and deduplicates job listings from Indeed India and Naukri.com.

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
Scheduler → Worker → Scraper → Extraction → Cleaning → Normalization → Deduplication → Output
```

## Sources

| Source   | Method      | Status     |
|----------|-------------|------------|
| Naukri   | JSON API    | ✅ Active  |
| Indeed   | Playwright  | ✅ Active  |
| LinkedIn | Playwright  | 🔜 Phase 1 |

## Output

Jobs are written to the database by default. If `OUTPUT_FORMATS` is set to `json,csv`, they will also be written to `output/final/` as timestamped files.

## Configuration

Copy `.env.example` to `.env` and adjust values. All settings have sensible defaults for dev mode.

## Key environment variables

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

## Registry output

When `USE_REGISTRY=true`, the pipeline writes deduplicated jobs to the shared `JobRegistry`
in addition to the normal JSON/CSV files. The registry file is created automatically.

```bash
USE_REGISTRY=true python -m dev_mode.dev_runner
```

Or in code:

```python
from scraper.config import Config
from scraper.pipeline.pipeline import ScraperPipeline

pipeline = ScraperPipeline(Config(use_registry=True))
```

## Running specific scrapers

```python
from dev_mode.dev_runner import DevModeRunner
import asyncio

runner = DevModeRunner()

# Naukri only
asyncio.run(runner.run_naukri_scraper(keywords=["Python Developer"], locations=["Bangalore"]))

# Indeed only
asyncio.run(runner.run_indeed_scraper(keywords=["Data Analyst"], locations=["Mumbai"]))

# Full pipeline
asyncio.run(runner.run_full_pipeline("naukri", keywords=["Django"], locations=["Hyderabad"]))
```

## Interactive debugger

```bash
python -m dev_mode.interactive_debugger
# Commands: clean | normalize | quit
```

## Validate output

```bash
python scripts/validate_output.py
```

## Code quality

```bash
.venv/bin/black --check scraper/     # formatting
.venv/bin/flake8 scraper/            # linting
.venv/bin/pytest tests/ -v           # tests
```

## Phase 0 limitations

- LinkedIn scraper is a stub (returns empty list) — full implementation in Phase 1
- Indeed Scraper uses playwright-stealth to bypass Cloudflare; may still be blocked on heavily restricted networks

## Redis Worker

The `scraper_worker/worker.py` process listens on the `scraper:tasks` Redis queue using `BLPOP`. It runs the full scraper pipeline on each task received.

```bash
# Requires REDIS_URL set in .env
python -m scraper_worker.worker
```

In Docker, this is the default `CMD` for the `scraper` container. Tasks are enqueued by the Admin API (`admin_api/scraper/service.py`) when a scraper is triggered from the Admin Console.
