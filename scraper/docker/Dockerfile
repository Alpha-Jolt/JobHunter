FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium --with-deps

COPY scraper/ ./scraper/
COPY dev_mode/ ./dev_mode/
COPY admin_dashboard/ ./admin_dashboard/
COPY data_collector_ui/ ./data_collector_ui/
COPY config/ ./config/

RUN mkdir -p logs output/raw output/processed output/final

CMD ["python", "-m", "dev_mode.dev_runner"]
