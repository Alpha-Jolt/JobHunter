import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import jwt from 'jsonwebtoken'
import { AuthService } from './auth.service'
import { ApiKeyService } from './apiKey.service'
import { authenticate, getRedisClient, ValidationError, AuthorizationError } from '@mail-bridge/shared'
import { AuthConfig } from './config'

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function createAuthRouter(pool: Pool, config: AuthConfig): Router {
  const router = Router()
  const service = new AuthService(pool, config)

  router.post('/register', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, password, workspace_name } = req.body as Record<string, string>
      if (!email || !password || !workspace_name) {
        throw new ValidationError('email, password, workspace_name are required', 'INVALID_PAYLOAD')
      }
      if (!validateEmail(email)) throw new ValidationError('Invalid email format', 'INVALID_EMAIL')
      if (password.length < 8) throw new ValidationError('Password must be at least 8 characters', 'WEAK_PASSWORD')

      const result = await service.register({ email, password, workspace_name })
      
      const apiKeyService = new ApiKeyService(pool)
      const defaultKey = await apiKeyService.create({
        workspaceId: result.workspace_id,
        userId: result.user_id,
        name: 'Default',
        scopes: ['send']
      })

      res.status(201).json({ 
        success: true, 
        ...result,
        api_key: {
          api_key_id: defaultKey.api_key_id,
          raw_key: defaultKey.raw_key,
          name: 'Default',
          scopes: ['send']
        }
      })
    } catch (err) { next(err) }
  })

  router.post('/login', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, password } = req.body as Record<string, string>
      if (!email || !password) throw new ValidationError('email and password are required', 'INVALID_PAYLOAD')

      const result = await service.login({ email, password })
      res.json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  router.post('/logout', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      const token = req.headers.authorization!.slice(7)
      await service.logout(token, getRedisClient())
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  router.post('/refresh', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { token } = req.body as { token?: string }
      if (!token) throw new ValidationError('token is required', 'INVALID_PAYLOAD')

      const result = await service.refresh(token)
      res.json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  router.post('/upgrade', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      if (req.user!.role !== 'owner') {
        throw new ValidationError('Only workspace owners can upgrade', 'FORBIDDEN')
      }
      if (req.user!.tier !== 'free') {
        throw new ValidationError('Workspace is already upgraded', 'ALREADY_UPGRADED')
      }

      const token = req.headers.authorization!.slice(7)
      const decoded = jwt.decode(token) as { email?: string } | null
      const email = decoded?.email ?? ''

      const result = await service.upgrade(req.user!.user_id, req.user!.workspace_id, email)
      res.json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  const apiKeyService = new ApiKeyService(pool)

  // API Key management routes - JWT only (enforced by checking apiKeyScopes)
  router.post('/api-keys', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      if (req.apiKeyScopes) throw new AuthorizationError('API keys can only be created using a JWT token', 'API_KEYS_REQUIRE_JWT')
      if (req.user!.role !== 'owner') throw new AuthorizationError('Only workspace owners can manage API keys', 'FORBIDDEN')

      const { name, scopes, expires_at } = req.body as { name?: string, scopes?: string[], expires_at?: string }
      if (!name) throw new ValidationError('name is required', 'INVALID_PAYLOAD')

      const result = await apiKeyService.create({
        workspaceId: req.user!.workspace_id,
        userId: req.user!.user_id,
        name,
        scopes,
        expiresAt: expires_at ? new Date(expires_at) : undefined
      })
      res.status(201).json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  router.get('/api-keys', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      if (req.apiKeyScopes) throw new AuthorizationError('API keys can only be listed using a JWT token', 'API_KEYS_REQUIRE_JWT')
      if (req.user!.role !== 'owner') throw new AuthorizationError('Only workspace owners can manage API keys', 'FORBIDDEN')

      const keys = await apiKeyService.list(req.user!.workspace_id)
      res.json({ success: true, api_keys: keys })
    } catch (err) { next(err) }
  })

  router.get('/api-keys/:id', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      if (req.apiKeyScopes) throw new AuthorizationError('API keys can only be retrieved using a JWT token', 'API_KEYS_REQUIRE_JWT')
      if (req.user!.role !== 'owner') throw new AuthorizationError('Only workspace owners can manage API keys', 'FORBIDDEN')

      const key = await apiKeyService.getById(req.params.id, req.user!.workspace_id)
      if (!key) throw new ValidationError('API key not found', 'NOT_FOUND')
      res.json({ success: true, ...key })
    } catch (err) { next(err) }
  })

  router.delete('/api-keys/:id', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      if (req.apiKeyScopes) throw new AuthorizationError('API keys can only be revoked using a JWT token', 'API_KEYS_REQUIRE_JWT')
      if (req.user!.role !== 'owner') throw new AuthorizationError('Only workspace owners can manage API keys', 'FORBIDDEN')

      await apiKeyService.revoke(req.params.id, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  return router
}
