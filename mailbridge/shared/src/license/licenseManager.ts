import crypto from 'crypto';

declare const __LICENSE_SIGNING_KEY__: string; // injected by esbuild

const CHANGE_DATE = new Date('2029-06-28');

export async function validateLicense(): Promise<void> {
  // Auto-pass after change date (Apache 2.0 mode)
  if (new Date() >= CHANGE_DATE) return;

  const key = process.env.MAIL_BRIDGE_LICENSE_KEY;
  if (!key) {
    console.error('[Mail-Bridge] MAIL_BRIDGE_LICENSE_KEY is not set.');
    console.error('[Mail-Bridge] Obtain a free key at: https://mail-bridge.io/license');
    process.exit(1);
  }

  const parts = key.split('-');
  if (parts.length !== 5 || parts[0] !== 'MAILBRIDGE') {
    console.error('[Mail-Bridge] Invalid license key format.');
    process.exit(1);
  }

  const [, type, yyyymm, payload, hmac8] = parts;

  // Check expiry from YYYYMM
  const issued = new Date(`${yyyymm.slice(0, 4)}-${yyyymm.slice(4, 6)}-01`);
  const expiry = new Date(issued);
  expiry.setFullYear(expiry.getFullYear() + 1); // FREE keys: 1-year validity
  if (new Date() > expiry) {
    console.error('[Mail-Bridge] License key has expired. Renew at https://mail-bridge.io/license');
    process.exit(1);
  }

  let signingKey = 'fallback_key';
  if (typeof __LICENSE_SIGNING_KEY__ !== 'undefined') {
    signingKey = __LICENSE_SIGNING_KEY__;
  } else if (process.env.LICENSE_SIGNING_KEY) {
    signingKey = process.env.LICENSE_SIGNING_KEY;
  }

  // Verify HMAC signature
  const computed = crypto
    .createHmac('sha256', signingKey)
    .update(`${type}-${yyyymm}-${payload}`)
    .digest('hex')
    .substring(0, 8);

  if (computed !== hmac8) {
    console.error('[Mail-Bridge] Invalid license key — signature mismatch.');
    process.exit(1);
  }

  // TODO(online-mode): POST to https://mail-bridge.io/api/v1/license/validate
  // for revocation checks and usage telemetry in a future release.
}
