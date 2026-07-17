# @mail-bridge/shared

<!-- TODO: shared is not published to npm — each service Dockerfile must build shared in the builder stage and manually copy shared/dist + shared/package.json into node_modules/@mail-bridge/shared in the production stage. Consider publishing shared as a private package or using a multi-stage monorepo build to avoid this. -->

## Overview

Shared library consumed by all Mail-Bridge microservices via npm workspaces. Provides centralized logging, error handling, exception handling, authentication middleware, authorization middleware, database pool, and Redis queue — ensuring consistency across all services with zero duplication.

## Key Capabilities

- **Centralized logging** — single Pino logger instance; all services import from here
- **Typed error hierarchy** — `AppError` subclasses map to HTTP status codes; never raw `Error`
- **Global exception handling** — `uncaughtException` and `unhandledRejection` handlers prevent silent crashes
- **JWT authentication middleware** — verifies Bearer token, checks Redis blocklist, attaches `req.user`
- **Authorization middleware** — `requireTier()` and `requireRole()` factories; handles Free/Pro flat roles and Enterprise RBAC
- **PostgreSQL pool** — lazy singleton `pg.Pool`; shared across all queries in a service
- **Redis email queue** — LPUSH/BRPOP FIFO queue with `enqueue()` and `dequeue()` helpers
- **Shared credential crypto** — `encryptCredential` / `decryptCredential` (AES-256-GCM + HKDF); single source of truth used by all services
- **Outlook OAuth helper** — `getOutlookAccessToken()` — decrypts token, refreshes if expired, writes back to DB

## Quick Start

```bash
# Consumed automatically via npm workspaces — no manual install needed
# Import in any service:
import { logger, AppError, authenticate, getPool, enqueue } from '@mail-bridge/shared'
```

## Architecture Overview

```
@mail-bridge/shared/src/
├── config.ts                    # Shared env var loader
├── models/types.ts              # All domain TypeScript interfaces
├── crypto/credentialCrypto.ts   # AES-256-GCM encrypt/decrypt (shared)
├── providers/outlookOAuth.ts    # Outlook token refresh + write-back
├── db/pool.ts                   # pg Pool singleton
├── queue/emailQueue.ts          # Redis LPUSH/BRPOP queue
└── features/
    ├── logging/logger.ts        # Pino singleton
    ├── error-handling/          # errors.ts + errorHandler.ts
    ├── exception-handling/      # exceptionHandler.ts
    ├── auth/auth.middleware.ts  # JWT verify + blocklist check
    └── authz/authz.middleware.ts # requireTier + requireRole
```

## API Reference

### Logging
```typescript
import { logger } from '@mail-bridge/shared'
logger.info({ userId, req_id }, 'user registered')
logger.error({ err, credentialId }, 'decrypt failed')
```

### Error Hierarchy
```typescript
import { ValidationError, AuthenticationError, NotFoundError } from '@mail-bridge/shared'
throw new ValidationError('email is required', 'MISSING_EMAIL')   // 400
throw new AuthenticationError('invalid token', 'INVALID_TOKEN')   // 401
throw new NotFoundError('credential not found')                    // 404
```

### Auth Middleware
```typescript
import { authenticate } from '@mail-bridge/shared'
router.get('/protected', authenticate, handler)
// req.user = { user_id, workspace_id, tier, role }
```

### Authz Middleware
```typescript
import { requireTier, requireRole } from '@mail-bridge/shared'
router.post('/send', authenticate, requireTier('free'), requireRole('member'), handler)
```

### Database Pool
```typescript
import { getPool } from '@mail-bridge/shared'
const pool = getPool()
const result = await pool.query('SELECT * FROM users WHERE user_id = $1', [id])
```

### Email Queue
```typescript
import { enqueue, dequeue } from '@mail-bridge/shared'
await enqueue({ emailLogId, credentialId, workspaceId, to, from, subject, html })
const job = await dequeue(5)  // blocks up to 5s
```
> **Resilience Note**: The shared Redis client attaches an `error` event listener to prevent unhandled rejections from crashing services during temporary Redis outages (e.g., `ECONNREFUSED` on container restarts).

### Credential Crypto
```typescript
import { encryptCredential, decryptCredential } from '@mail-bridge/shared'
const ciphertext = encryptCredential(plaintext, masterKey, keyId)
const plaintext  = decryptCredential(ciphertext, masterKey, keyId)
```

### Outlook OAuth Helper
```typescript
import { getOutlookAccessToken } from '@mail-bridge/shared'
// Decrypts token, refreshes if expired, writes back to DB automatically
const accessToken = await getOutlookAccessToken(encryptedValue, credentialId, keyId, config, pool)
```

### Exception Handlers
```typescript
import { registerExceptionHandlers } from '@mail-bridge/shared'
registerExceptionHandlers()  // call once at server bootstrap
```

## Configuration

Reads from environment variables via `getSharedConfig()`:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | No | Redis URL (default: `redis://localhost:6379`) |
| `JWT_SECRET` | Yes | JWT signing secret |
| `JWT_EXPIRES_IN` | No | Token TTL (default: `24h`) |
| `CREDENTIAL_MASTER_KEY` | Yes | 64 hex chars for AES-256-GCM |
| `LOG_LEVEL` | No | Pino log level (default: `info`) |

## Dependencies

### Required
- `pg 8.11.3` — PostgreSQL client
- `ioredis 5.3.2` — Redis client
- `jsonwebtoken 9.0.2` — JWT verification
- `pino 8.17.0` — structured logging
- `dotenv 16.3.1` — env loading
- `@azure/msal-node 2.9.2` — Outlook token refresh

### Optional
- `pino-pretty 10.3.1` — colored dev logs (dev only, graceful fallback)
