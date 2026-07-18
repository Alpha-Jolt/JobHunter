import { logger } from '../logging'

// Postgres error codes that are transient and should not crash the process
const TRANSIENT_PG_CODES = new Set([
  '57P01', // terminating connection due to administrator command
  '57P02', // crash shutdown
  '57P03', // cannot connect now
  '08006', // connection failure
  '08001', // unable to connect
  '08004', // rejected connection
])

function isTransientError(err: unknown): boolean {
  if (err && typeof err === 'object') {
    const code = (err as { code?: string }).code
    if (code && TRANSIENT_PG_CODES.has(code)) return true
    const msg = (err as { message?: string }).message ?? ''
    if (msg.includes('ECONNREFUSED') || msg.includes('ECONNRESET') || msg.includes('ETIMEDOUT')) return true
  }
  return false
}

export function registerExceptionHandlers(): void {
  process.on('uncaughtException', (err: Error) => {
    if (isTransientError(err)) {
      logger.warn({ err }, 'Transient connection error — process continues')
      return
    }
    logger.fatal({ err }, 'Uncaught exception — shutting down')
    process.exit(1)
  })

  process.on('unhandledRejection', (reason: unknown) => {
    if (isTransientError(reason)) {
      logger.warn({ reason }, 'Transient connection rejection — process continues')
      return
    }
    logger.fatal({ reason }, 'Unhandled promise rejection — shutting down')
    process.exit(1)
  })
}
