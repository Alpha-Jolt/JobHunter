import * as dotenv from 'dotenv'
dotenv.config()

export interface CredentialsConfig {
  port: number
  nodeEnv: string
  databaseUrl: string
  redisUrl: string
  jwtSecret: string
  credentialMasterKey: string
  gmailClientId: string
  gmailClientSecret: string
  gmailRedirectUri: string
  gmailPubSubTopic: string
  outlookClientId: string
  outlookClientSecret: string
  outlookRedirectUri: string
  outlookTenantId: string
  logLevel: string
}

export function getConfig(): CredentialsConfig {
  return {
    port: parseInt(process.env.PORT ?? '3002'),
    nodeEnv: process.env.NODE_ENV ?? 'development',
    databaseUrl: process.env.DATABASE_URL ?? '',
    redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
    jwtSecret: process.env.JWT_SECRET ?? '',
    credentialMasterKey: process.env.CREDENTIAL_MASTER_KEY ?? '',
    gmailClientId: process.env.GMAIL_CLIENT_ID ?? '',
    gmailClientSecret: process.env.GMAIL_CLIENT_SECRET ?? '',
    gmailRedirectUri: process.env.GMAIL_REDIRECT_URI ?? 'http://localhost:3002/api/credentials/gmail/callback',
    gmailPubSubTopic: process.env.GMAIL_PUBSUB_TOPIC ?? '',
    outlookClientId: process.env.OUTLOOK_CLIENT_ID ?? '',
    outlookClientSecret: process.env.OUTLOOK_CLIENT_SECRET ?? '',
    outlookRedirectUri: process.env.OUTLOOK_REDIRECT_URI ?? 'http://localhost:3002/api/credentials/outlook/callback',
    outlookTenantId: process.env.OUTLOOK_TENANT_ID ?? 'common',
    logLevel: process.env.LOG_LEVEL ?? 'info'
  }
}
