import { ConfidentialClientApplication } from '@azure/msal-node'
import { CredentialsConfig } from './config'
import { OutlookTokenBundle } from '@mail-bridge/shared'

export function buildOutlookApp(config: CredentialsConfig): ConfidentialClientApplication {
  return new ConfidentialClientApplication({
    auth: {
      clientId: config.outlookClientId,
      clientSecret: config.outlookClientSecret,
      authority: `https://login.microsoftonline.com/${config.outlookTenantId}`
    }
  })
}

export async function getOutlookConsentUrl(config: CredentialsConfig, state: string): Promise<string> {
  const app = buildOutlookApp(config)
  return await app.getAuthCodeUrl({
    scopes: ['https://graph.microsoft.com/Mail.Send', 'https://graph.microsoft.com/Mail.Read', 'offline_access'],
    redirectUri: config.outlookRedirectUri,
    state
  })
}

export async function exchangeOutlookCode(
  code: string,
  config: CredentialsConfig
): Promise<OutlookTokenBundle> {
  const app = buildOutlookApp(config)
  const result = await app.acquireTokenByCode({
    code,
    scopes: ['https://graph.microsoft.com/Mail.Send', 'https://graph.microsoft.com/Mail.Read', 'offline_access'],
    redirectUri: config.outlookRedirectUri
  })

  if (!result?.accessToken) {
    throw new Error('Outlook code exchange failed: no access token')
  }

  return {
    access_token: result.accessToken,
    refresh_token: (result as unknown as { refreshToken?: string }).refreshToken ?? '',
    expires_at: result.expiresOn ? result.expiresOn.getTime() : Date.now() + 3600 * 1000
  }
}
