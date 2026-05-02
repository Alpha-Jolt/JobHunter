FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY scraper/requirements.txt ./scraper/requirements.txt

RUN pip install --no-cache-dir -r scraper/requirements.txt

RUN playwright install chromium --with-deps

COPY scraper/scraper/ ./scraper/
COPY scraper/dev_mode/ ./dev_mode/
COPY scraper/admin_dashboard/ ./admin_dashboard/
COPY scraper/data_collector_ui/ ./data_collector_ui/
COPY scraper/config/ ./config/

RUN mkdir -p logs output/raw output/processed output/final registries

CMD ["python", "-m", "dev_mode.dev_runner"]
