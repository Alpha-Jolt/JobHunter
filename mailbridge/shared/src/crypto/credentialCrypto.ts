import { createCipheriv, createDecipheriv, hkdfSync, randomBytes } from 'crypto'

const ALGORITHM = 'aes-256-gcm'
const IV_LENGTH = 12
const AUTH_TAG_LENGTH = 16

function deriveKey(masterKey: string, keyId: string): Buffer {
  const master = Buffer.from(masterKey, 'hex')
  return Buffer.from(
    hkdfSync('sha256', master, Buffer.from(keyId), Buffer.from('mail-bridge-credential'), 32)
  )
}

export function encryptCredential(plaintext: string, masterKey: string, keyId: string): string {
  const key = deriveKey(masterKey, keyId)
  const iv = randomBytes(IV_LENGTH)
  const cipher = createCipheriv(ALGORITHM, key, iv)
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()])
  const authTag = cipher.getAuthTag()
  return Buffer.concat([iv, authTag, encrypted]).toString('base64')
}

export function decryptCredential(ciphertext: string, masterKey: string, keyId: string): string {
  const key = deriveKey(masterKey, keyId)
  const buf = Buffer.from(ciphertext, 'base64')
  const iv = buf.subarray(0, IV_LENGTH)
  const authTag = buf.subarray(IV_LENGTH, IV_LENGTH + AUTH_TAG_LENGTH)
  const encrypted = buf.subarray(IV_LENGTH + AUTH_TAG_LENGTH)
  const decipher = createDecipheriv(ALGORITHM, key, iv)
  decipher.setAuthTag(authTag)
  return decipher.update(encrypted) + decipher.final('utf8')
}
