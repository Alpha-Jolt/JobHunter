#!/bin/bash
set -e

MINIO_ENDPOINT="${MINIO_ENDPOINT:-localhost:9000}"
MINIO_USER="${MINIO_USER:-minioadmin}"
MINIO_PASS="${MINIO_PASS:-minioadmin}"
BUCKET_NAME="${BUCKET_NAME:-jobhunter-resumes}"

echo "Waiting for MinIO to be ready..."
until curl -sf "http://$MINIO_ENDPOINT/minio/health/live" > /dev/null 2>&1; do
  echo "  MinIO not ready yet..."
  sleep 2
done
echo "MinIO is ready!"

if ! command -v mc &> /dev/null; then
  echo "Installing MinIO client (mc)..."
  curl -s https://dl.min.io/client/mc/release/linux-amd64/mc \
    --create-dirs -o "$HOME/minio-binaries/mc"
  chmod +x "$HOME/minio-binaries/mc"
  export PATH="$PATH:$HOME/minio-binaries"
fi

echo "Creating bucket '$BUCKET_NAME'..."
mc alias set local "http://$MINIO_ENDPOINT" "$MINIO_USER" "$MINIO_PASS"
mc mb "local/$BUCKET_NAME" --ignore-existing

echo "MinIO setup complete!"
echo "Web Console: http://localhost:9001"
echo "API Endpoint: http://localhost:9000"
