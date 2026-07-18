import * as dotenv from 'dotenv'
dotenv.config()

export interface AuthConfig {
  port: number
  nodeEnv: string
  databaseUrl: string
  redisUrl: string
  jwtSecret: string
  jwtExpiresIn: string
  logLevel: string
}

export function getConfig(): AuthConfig {
  return {
    port: parseInt(process.env.PORT ?? '3001'),
    nodeEnv: process.env.NODE_ENV ?? 'development',
    databaseUrl: process.env.DATABASE_URL ?? '',
    redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
    jwtSecret: process.env.JWT_SECRET ?? '',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN ?? '24h',
    logLevel: process.env.LOG_LEVEL ?? 'info'
  }
}
