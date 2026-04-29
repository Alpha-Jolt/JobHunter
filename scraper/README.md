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

# 4. Admin dashboard
uvicorn admin_dashboard.app:app --port 8001 --reload

# 5. Data collector UI
uvicorn data_collector_ui.app:app --port 8002 --reload
```

## Install as package

```bash
pip install -e ".[dev]"
```

## Docker

```bash
cd docker
docker compose up --build
# scraper on dev_runner, admin on :8001, data collector on :8002
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

Jobs are written to `output/final/` as timestamped JSON and CSV files.

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
| `OUTPUT_FORMATS` | `json,csv` | Output file formats |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `PROXY_LIST` | _(empty)_ | Comma-separated proxy URLs |

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
- Database output raises `NotImplementedError` — PostgreSQL integration in Phase 0+
- Redis scheduler requires a running Redis instance — not needed for `dev_runner`
