import express from 'express'
import { Redis } from 'ioredis'
import { getPool, errorHandler, registerExceptionHandlers, logger, validateLicense } from '@mail-bridge/shared'
import { createWebhooksRouter } from './webhooks.routes'
import { WebhooksService } from './webhooks.service'
import { startWebhookSubscriber, startRetryLoop } from './webhookDispatcher'
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
  app.use('/api/webhooks', createWebhooksRouter(pool, config))
  app.use(errorHandler)

  // Redis subscriber (separate connection — cannot use same connection for pub+sub)
  const subscriber = new Redis(config.redisUrl)
  const service = new WebhooksService(pool, config.credentialMasterKey)
  startWebhookSubscriber(subscriber, service, pool)
  startRetryLoop(service, pool)

  app.listen(config.port, () => {
    logger.info({ port: config.port, service: 'webhooks' }, 'Webhooks service started')
  })
}

startServer().catch(err => {
  logger.error(err, 'Failed to start webhooks service')
  process.exit(1)
})
