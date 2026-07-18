import pino from 'pino'
import { getSharedConfig } from '../../config'

const config = getSharedConfig()

function buildTransport(): pino.TransportSingleOptions | undefined {
  if (config.nodeEnv !== 'development') return undefined
  try {
    require.resolve('pino-pretty')
    return { target: 'pino-pretty', options: { colorize: true, translateTime: 'SYS:standard' } }
  } catch {
    return undefined
  }
}

export const logger = pino({
  level: config.logLevel,
  transport: buildTransport()
})
