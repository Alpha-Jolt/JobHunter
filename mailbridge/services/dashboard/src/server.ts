import express from 'express'
import { getPool, errorHandler, registerExceptionHandlers, logger } from '@mail-bridge/shared'
import { createDashboardRouter } from './dashboard.routes'
import { getConfig } from './config'

registerExceptionHandlers()

const config = getConfig()
const app = express()
app.use(express.json())

app.use((req, _res, next) => {
  req.id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
  next()
})

const pool = getPool()
app.use('/', createDashboardRouter(pool))
app.use(errorHandler)

app.listen(config.port, () => {
  logger.info({ port: config.port, service: 'dashboard' }, 'Dashboard service started')
})

export { app }
