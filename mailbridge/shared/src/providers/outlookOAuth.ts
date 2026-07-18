import { ConfidentialClientApplication } from '@azure/msal-node'
import { Pool } from 'pg'
import { encryptCredential, decryptCredential } from '../crypto/credentialCrypto'

export interface OutlookTokenBundle {
  access_token: string
  refresh_token: string
  expires_at: number // unix ms
}

export interface OutlookConfig {
  clientId: string
  clientSecret: string
  tenantId: string
  masterKey: string
}

function buildMsalApp(config: OutlookConfig): ConfidentialClientApplication {
  return new ConfidentialClientApplication({
    auth: {
      clientId: config.clientId,
      clientSecret: config.clientSecret,
      authority: `https://login.microsoftonline.com/${config.tenantId}`
    }
  })
}

/**
 * Decrypt stored credential, check expiry, refresh if needed.
 * If refreshed, re-encrypts and writes back to DB.
 * Returns a valid access token.
 */
export async function getOutlookAccessToken(
  encryptedValue: string,
  credentialId: string,
  keyId: string,
  config: OutlookConfig,
  pool: Pool
): Promise<string> {
  const bundle: OutlookTokenBundle = JSON.parse(
    decryptCredential(encryptedValue, config.masterKey, keyId)
  )

  // Return existing token if still valid (5 min buffer)
  if (bundle.expires_at - Date.now() > 5 * 60 * 1000) {
    return bundle.access_token
  }

  return _refreshAndPersist(bundle, credentialId, keyId, config, pool)
}

async function _refreshAndPersist(
  bundle: OutlookTokenBundle,
  credentialId: string,
  keyId: string,
  config: OutlookConfig,
  pool: Pool
): Promise<string> {
  const msalApp = buildMsalApp(config)

  const result = await msalApp.acquireTokenByRefreshToken({
    refreshToken: bundle.refresh_token,
    scopes: ['https://graph.microsoft.com/Mail.Send']
  })

  if (!result?.accessToken) {
    throw new Error('Outlook token refresh failed: no access token returned')
  }

  const newBundle: OutlookTokenBundle = {
    access_token: result.accessToken,
    refresh_token: bundle.refresh_token,
    expires_at: result.expiresOn ? result.expiresOn.getTime() : Date.now() + 3600 * 1000
  }

  const newEncrypted = encryptCredential(JSON.stringify(newBundle), config.masterKey, keyId)

  await pool.query(
    'UPDATE credentials SET encrypted_value = $1, last_used_at = NOW() WHERE credential_id = $2',
    [newEncrypted, credentialId]
  )

  return newBundle.access_token
}
