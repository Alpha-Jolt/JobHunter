FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev git \
    fonts-unifont \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 \
    libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY scraper/requirements.txt ./scraper/requirements.txt

RUN pip install --no-cache-dir --timeout 300 --retries 5 -r scraper/requirements.txt

RUN playwright install chromium

COPY scraper/scraper/ ./scraper/
COPY scraper/dev_mode/ ./dev_mode/
COPY scraper/config/ ./config/
COPY scraper/scraper_worker/ ./scraper_worker/

RUN mkdir -p logs output/raw output/processed output/final registries

CMD ["python", "-m", "scraper_worker.worker"]
