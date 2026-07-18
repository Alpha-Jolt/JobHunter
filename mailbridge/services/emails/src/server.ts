import express from 'express'
import { getPool, errorHandler, registerExceptionHandlers, logger, validateLicense } from '@mail-bridge/shared'
import { createEmailsRouter } from './emails.routes'
import { createInboundRouter } from './inbound.routes'
import { startScheduler } from './scheduler'
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
  app.use('/api/emails', createEmailsRouter(pool, config))
  app.use('/api/inbound', createInboundRouter(pool))
  app.use(errorHandler)

  startScheduler(pool)

  app.listen(config.port, () => {
    logger.info({ port: config.port, service: 'emails' }, 'Emails service started')
  })
}

startServer().catch(err => {
  logger.error(err, 'Failed to start emails service')
  process.exit(1)
})
