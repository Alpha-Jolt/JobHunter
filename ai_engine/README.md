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

---

## Supported LLM Providers

Anthropic (claude-sonnet-4-5), OpenAI (gpt-4o-mini), Gemini (gemini-2.0-flash), DeepSeek (deepseek-chat), Grok (grok-3), OpenRouter (configurable model).

---

## Running Tests

```bash
pytest
```

---

## License

See [LICENSE](../LICENSE)
