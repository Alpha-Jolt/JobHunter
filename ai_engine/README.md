# JobHunter AI Engine

Intelligent resume curation and job application engine for the JobHunter platform. Given a candidate's resume and a batch of scraped job listings, it analyses each job, compares the resume against it, generates a tailored variant, and produces a ready-to-send output package (DOCX resume, cover letter, email draft).

---

## Requirements

- Python 3.12+
- LibreOffice (headless, for PDF rendering)
- At least one LLM provider API key

---

## Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r ai_engine/requirements.txt
cp ai_engine/.env.example .env   # then fill in your API key(s)
```

---

## Usage

```python
from ai_engine.features.orchestration.pipeline import Pipeline
from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig
from ai_engine.core.types import PipelineMode

config = PipelineConfig(
    resume_file_path="path/to/resume.pdf",
    user_id="user-123",
    session_id="session-001",
    mode=PipelineMode.GENERATE,
)
result = await pipeline.run(config)
# result.variant_ids — pending approval
```

---

## Pipeline Modes

**Generate** — ingests scraper output, parses resume, analyses each job, compares, optimises, registers variants. All variants are left pending approval.

**Release** — for each approved variant: checks the approval gate, renders DOCX resume, generates cover letter, fills email template, writes output package to `ai_output/`.

---

## Key Guarantees

- **No fabrication** — every LLM output is validated against the source resume by a deterministic set-operation check. Fabricated content is rejected, never silently passed through.
- **Approval gate** — no file is written to disk unless the variant is explicitly approved.
- **Variant budget** — generation stops hard at `MAX_VARIANTS_TOTAL` / `MAX_VARIANTS_PER_SESSION`.
- **Provider agnosticism** — swap LLM providers by changing one `.env` variable. No code changes.

---

## Configuration

Copy `ai_engine/.env.example` to `.env` and set at minimum one provider key.

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `LLM_PRIMARY_PROVIDER` | `anthropic` | Active primary provider |
| `MAX_VARIANTS_TOTAL` | `50` | Hard global variant cap |
| `MAX_VARIANTS_PER_SESSION` | `10` | Per-session cap |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` |
| `USE_SHARED_REGISTRY` | `false` | Read jobs from / write variants to `shared` registries |
| `SHARED_JOBS_REGISTRY_PATH` | `registries/jobs.json` | Path to shared jobs registry |
| `SHARED_VARIANTS_REGISTRY_PATH` | `registries/variants.json` | Path to shared variants registry |
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO API endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `MINIO_BUCKET_NAME` | `jobhunter-resumes` | S3 bucket for resume files |
| `MINIO_ENABLED` | `true` | Enable S3 uploads; falls back to local on failure |

---

## Supported LLM Providers

Anthropic (claude-sonnet-4-5), OpenAI (gpt-4o-mini), Gemini (gemini-2.0-flash), DeepSeek (deepseek-chat), Grok (grok-3), OpenRouter (configurable model).

---

## Docker

```bash
# From the project root
docker compose -f DOCKER-COMPOSE.yml up --build ai_engine
```

The container loads configuration from `ai_engine/.env`. Copy `ai_engine/.env.example` to `ai_engine/.env` and set at least one LLM provider key before building.

---

## Shared Registry Integration

When `USE_SHARED_REGISTRY=true`, the AI Engine reads jobs from `shared.JobRegistry`
instead of CSV/JSON files, and writes variants to `shared.VariantRegistry` instead of
its internal JSON registry. Both integrations are off by default.

```bash
USE_SHARED_REGISTRY=true python -m ai_engine.features.orchestration.pipeline
```

Or in code:

```python
from ai_engine.features.orchestration.models.pipeline_config import PipelineConfig

config = PipelineConfig(
    resume_file_path="resume.pdf",
    user_id="user-123",
    session_id="session-001",
    use_shared_registry=True,
)
```

---

## MinIO S3 Storage

When `MINIO_ENABLED=true`, `OutputBuilder` uploads rendered resume PDFs, DOCX files, and cover letters to MinIO after generation. S3 keys are stored on `VariantRecord` (`pdf_key`, `docx_key`, `cover_letter_key`). If the upload fails, the builder falls back to local paths and sets `s3_upload_failed=True` on the `OutputPackage`.

### S3 key format

```
resumes/{user_id}/{job_id}/{YYYYMMDD_HHMMSS}_{file_type}.{ext}
```

### Start MinIO

```bash
# From project root
docker compose -f DOCKER-COMPOSE.yml up -d minio
bash scripts/setup_minio.sh
# Console: http://localhost:9001  (minioadmin / minioadmin)
```

---

## Running Tests

```bash
pytest
```

---

## License

See [LICENSE](../LICENSE)
