# gateway

## Overview

Nginx reverse proxy that sits in front of all Mail-Bridge microservices. Provides a single entry point on port 3009, enforces rate limiting, injects device fingerprint headers, and routes requests to the correct upstream service.

## Key Capabilities

- Single ingress point for all API traffic
- Rate limiting: 5 req/min on auth routes, 100 req/s on API routes
- Device fingerprint header injection (`X-Device-Fingerprint`) for audit logging
- Upstream routing to all 7 backend services
- Connection keep-alive and proxy buffering

## Architecture Overview

```
Client → :3009 (Nginx)
  /auth/*              → auth:3001
  /api/credentials/*   → credentials:3002
  /api/emails/*        → emails:3003
  /api/templates/*     → templates:3004
  /api/admin/*         → admin:3005
  /health/*            → health:3006
  /api/webhooks/*      → webhooks:3008
```

> **Routing Note:** The gateway uses strict prefix matching without trailing slashes (e.g. `location /api/templates`) and `proxy_pass` without a trailing slash to prevent implicit `301 Moved Permanently` redirects that would cause `POST` requests to downgrade to `GET`.

## Configuration

| Directive | Value | Purpose |
|---|---|---|
| `limit_req_zone auth` | 5r/m | Brute-force protection on login/register |
| `limit_req_zone api` | 100r/s | General API rate limit |
| `proxy_set_header X-Device-Fingerprint` | `$http_user_agent-$remote_addr` | Device audit trail |
| `proxy_set_header X-Real-IP` | `$remote_addr` | Upstream IP forwarding |

## Quick Start

```bash
# Docker
docker build -t mb-gateway ./gateway
docker run -p 3009:3009 mb-gateway

# Docker Compose
docker-compose up -d gateway
```

## Dependencies

- `nginx:1.25-alpine` — base image

## Known Limitations

- No TLS termination in Phase 1 — add SSL certificates for production
- Device fingerprint is a simple hash of user-agent + IP, not a full fingerprint
- No authentication at the gateway layer — auth is handled per-service
