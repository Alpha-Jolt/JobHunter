import express from 'express'
import { getPool, errorHandler, registerExceptionHandlers, logger, validateLicense } from '@mail-bridge/shared'
import { createAuthRouter } from './auth.routes'
import { getConfig } from './config'

registerExceptionHandlers()

async function startServer() {
  await validateLicense()

  const config = getConfig()
  const app = express()
  app.use(express.json())

  // Attach request ID for log tracing
  app.use((req, _res, next) => {
    req.id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    next()
  })

  const pool = getPool()
  app.use('/auth', createAuthRouter(pool, config))

  app.use(errorHandler)

  app.listen(config.port, () => {
    logger.info({ port: config.port, service: 'auth' }, 'Auth service started')
  })
}

startServer().catch(err => {
  logger.error(err, 'Failed to start auth service')
  process.exit(1)
})
