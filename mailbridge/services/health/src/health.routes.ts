import { Router, Request, Response } from 'express'
import { Pool } from 'pg'
import Redis from 'ioredis'

export function createHealthRouter(pool: Pool, redis: Redis): Router {
  const router = Router()

  router.get('/', (_req: Request, res: Response) => {
    res.json({ status: 'ok', version: '2.0.0', timestamp: new Date().toISOString() })
  })

  router.get('/ready', async (_req: Request, res: Response) => {
    const checks = await Promise.allSettled([
      pool.query('SELECT 1'),
      redis.ping()
    ])
    const db = checks[0].status === 'fulfilled' ? 'ok' : 'down'
    const redisStatus = checks[1].status === 'fulfilled' ? 'ok' : 'down'
    const ready = db === 'ok' && redisStatus === 'ok'
    res.status(ready ? 200 : 503).json({ status: ready ? 'ready' : 'not_ready', db, redis: redisStatus })
  })

  return router
}
