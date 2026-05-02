FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*

COPY ai_engine/requirements.txt ./ai_engine/requirements.txt
COPY shared/requirements.txt ./shared/requirements.txt

RUN pip install --no-cache-dir -r ai_engine/requirements.txt \
    && pip install --no-cache-dir -r shared/requirements.txt

COPY shared/ ./shared/
COPY ai_engine/ ./ai_engine/

RUN mkdir -p ai_output registries

ENV PYTHONPATH=/app

CMD ["python", "-m", "ai_engine.features.orchestration.pipeline"]
