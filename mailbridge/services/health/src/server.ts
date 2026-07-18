import express from 'express'
import { getPool, getRedisClient, errorHandler, registerExceptionHandlers, logger, validateLicense } from '@mail-bridge/shared'
import { createHealthRouter } from './health.routes'
import { getConfig } from './config'

registerExceptionHandlers()

async function startServer() {
  await validateLicense()

  const config = getConfig()
  const app = express()
  app.use(express.json())

  const pool = getPool()
  const redis = getRedisClient()
  app.use('/health', createHealthRouter(pool, redis))
  app.use(errorHandler)

  app.listen(config.port, () => {
    logger.info({ port: config.port, service: 'health' }, 'Health service started')
  })
}

startServer().catch(err => {
  logger.error(err, 'Failed to start health service')
  process.exit(1)
})
