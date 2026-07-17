#!/bin/bash
set -e

SERVICE=$1
if [ -z "$SERVICE" ]; then
  echo "Usage: $0 <service>"
  echo "Example: $0 auth"
  exit 1
fi

echo "Building local image for $SERVICE..."
docker build -f services/${SERVICE}/Dockerfile \
  --build-arg LICENSE_SIGNING_KEY=test_signing_key_local_dev \
  -t mailbridge-${SERVICE}:local .

echo "Done. Built mailbridge-${SERVICE}:local"
