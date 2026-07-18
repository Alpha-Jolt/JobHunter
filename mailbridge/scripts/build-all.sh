#!/bin/bash
set -e

if [ -z "$LICENSE_SIGNING_KEY" ]; then
  echo "Error: LICENSE_SIGNING_KEY environment variable is required."
  exit 1
fi

SERVICES="auth credentials emails templates admin health dashboard webhooks"

echo "Building API services..."
for SERVICE in $SERVICES; do
  echo "Building $SERVICE..."
  docker build -f services/${SERVICE}/Dockerfile \
    --build-arg LICENSE_SIGNING_KEY="$LICENSE_SIGNING_KEY" \
    -t ghcr.io/jobhunter2026/mailbridge-${SERVICE}:latest .
done

echo "Building gateway..."
docker build -f gateway/Dockerfile -t ghcr.io/jobhunter2026/mailbridge-gateway:latest gateway/

echo "Building webapp..."
docker build -f webapp/Dockerfile -t ghcr.io/jobhunter2026/mailbridge-webapp:latest webapp/

echo "Building website..."
docker build -f website/Dockerfile -t ghcr.io/jobhunter2026/mailbridge-website:latest website/

echo "All images built successfully."
