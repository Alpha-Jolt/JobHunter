export const config = {
  // Always same-origin in the browser. Next.js rewrites /api/* → INTERNAL_API_URL
  // (see next.config.ts). This avoids CORS and cross-subdomain cookie issues.
  // Do NOT point the browser at https://api.myjobhunter.in.
  apiBaseUrl: "",
  internalApiUrl: process.env.INTERNAL_API_URL ?? "http://localhost:8000",
  appUrl: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
} as const;
