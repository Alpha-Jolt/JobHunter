FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git curl libmagic1 libreoffice default-jre && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY orchestration/requirements.txt ./orchestration_requirements.txt
COPY ai_engine/requirements.txt ./ai_engine_requirements.txt
RUN pip install --no-cache-dir -r orchestration_requirements.txt -r ai_engine_requirements.txt

COPY orchestration/ ./orchestration/
COPY ai_engine/ ./ai_engine/
COPY alembic.ini ./

ENV PYTHONPATH=/app

CMD ["uvicorn", "orchestration.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
