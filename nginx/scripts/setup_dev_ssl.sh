#!/bin/bash
set -e

# Creates self-signed certificates for local development

DOMAIN="myjobhunter.in"
SSL_DIR="$(dirname "$0")/../ssl"
mkdir -p "$SSL_DIR"

if [ -f "$SSL_DIR/cert.pem" ]; then
    echo "SSL certificates already exist in $SSL_DIR"
    exit 0
fi

echo "Generating self-signed SSL certificate for $DOMAIN and *.$DOMAIN"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -subj "/C=US/ST=State/L=City/O=JobHunter/CN=$DOMAIN" \
    -addext "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN"

echo "Dev SSL setup complete!"
