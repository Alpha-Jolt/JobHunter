import * as dotenv from 'dotenv'
dotenv.config()

export interface DashboardConfig {
  port: number
  nodeEnv: string
  databaseUrl: string
  redisUrl: string
  jwtSecret: string
  logLevel: string
}

export function getConfig(): DashboardConfig {
  return {
    port: parseInt(process.env.PORT ?? '3007'),
    nodeEnv: process.env.NODE_ENV ?? 'development',
    databaseUrl: process.env.DATABASE_URL ?? '',
    redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
    jwtSecret: process.env.JWT_SECRET ?? '',
    logLevel: process.env.LOG_LEVEL ?? 'info'
  }
}
