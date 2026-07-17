import * as dotenv from 'dotenv'
dotenv.config()

export interface HealthConfig {
  port: number
  databaseUrl: string
  redisUrl: string
  logLevel: string
}

export function getConfig(): HealthConfig {
  return {
    port: parseInt(process.env.PORT ?? '3006'),
    databaseUrl: process.env.DATABASE_URL ?? '',
    redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
    logLevel: process.env.LOG_LEVEL ?? 'info'
  }
}
