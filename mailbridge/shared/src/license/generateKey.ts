import crypto from 'crypto';

function generateKey(type: string, signingKey: string): string {
  const now = new Date();
  const yyyymm = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}`;
  
  // payload could encode seats, tier, or exact expiry timestamp base62
  const payload = crypto.randomBytes(4).toString('hex');
  
  const hmac8 = crypto
    .createHmac('sha256', signingKey)
    .update(`${type}-${yyyymm}-${payload}`)
    .digest('hex')
    .substring(0, 8);
    
  return `MAILBRIDGE-${type}-${yyyymm}-${payload}-${hmac8}`;
}

const args = process.argv.slice(2);
const typeIndex = args.indexOf('--type');
const type = typeIndex !== -1 ? args[typeIndex + 1] : 'FREE';

const signingKey = process.env.LICENSE_SIGNING_KEY;
if (!signingKey) {
  console.error('Error: LICENSE_SIGNING_KEY environment variable is required to generate a key.');
  process.exit(1);
}

const key = generateKey(type, signingKey);
console.log(key);
