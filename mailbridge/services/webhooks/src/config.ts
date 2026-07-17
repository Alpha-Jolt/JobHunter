import * as dotenv from 'dotenv'
dotenv.config()

export interface WebhooksConfig {
  port: number
  nodeEnv: string
  databaseUrl: string
  redisUrl: string
  jwtSecret: string
  credentialMasterKey: string
  logLevel: string
}

export function getConfig(): WebhooksConfig {
  return {
    port: parseInt(process.env.PORT ?? '3008'),
    nodeEnv: process.env.NODE_ENV ?? 'development',
    databaseUrl: process.env.DATABASE_URL ?? '',
    redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
    jwtSecret: process.env.JWT_SECRET ?? '',
    credentialMasterKey: process.env.CREDENTIAL_MASTER_KEY ?? '',
    logLevel: process.env.LOG_LEVEL ?? 'info'
  }
}
