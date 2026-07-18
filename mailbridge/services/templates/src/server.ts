import express from 'express'
import { getPool, errorHandler, registerExceptionHandlers, logger, validateLicense } from '@mail-bridge/shared'
import { createTemplatesRouter } from './templates.routes'
import { getConfig } from './config'

registerExceptionHandlers()

async function startServer() {
  await validateLicense()

  const config = getConfig()
  const app = express()
  app.use(express.json())

  app.use((req, _res, next) => {
    req.id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    next()
  })

  const pool = getPool()
  app.use('/api/templates', createTemplatesRouter(pool))
  app.use(errorHandler)

  app.listen(config.port, () => {
    logger.info({ port: config.port, service: 'templates' }, 'Templates service started')
  })
}

startServer().catch(err => {
  logger.error(err, 'Failed to start templates service')
  process.exit(1)
})
