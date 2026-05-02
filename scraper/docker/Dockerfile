FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY scraper/requirements.txt ./scraper/requirements.txt
COPY shared/requirements.txt ./shared/requirements.txt

RUN pip install --no-cache-dir -r scraper/requirements.txt \
    && pip install --no-cache-dir -r shared/requirements.txt

RUN playwright install chromium --with-deps

COPY scraper/scraper/ ./scraper/
COPY scraper/dev_mode/ ./dev_mode/
COPY scraper/admin_dashboard/ ./admin_dashboard/
COPY scraper/data_collector_ui/ ./data_collector_ui/
COPY scraper/config/ ./config/
COPY shared/ ./shared/

RUN pip install --no-cache-dir -e ./shared/

RUN mkdir -p logs output/raw output/processed output/final registries

CMD ["python", "-m", "dev_mode.dev_runner"]
