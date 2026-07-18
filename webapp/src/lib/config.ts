export const config = {
  // Empty string = same-origin (browser calls /api/* on app host; Next.js rewrites
  // to INTERNAL_API_URL). Avoids cross-origin CORS and cookie Domain issues.
  // Set NEXT_PUBLIC_API_BASE_URL=same-origin (or empty) in production.
  // Local next dev: leave unset → http://localhost:8000
  apiBaseUrl: resolvePublicApiBaseUrl(),
  internalApiUrl:
    process.env.INTERNAL_API_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000",
  appUrl: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
} as const;

function resolvePublicApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (raw === undefined) return "http://localhost:8000";
  const normalized = raw.trim();
  if (
    normalized === "" ||
    normalized === "/" ||
    normalized === "same-origin"
  ) {
    return "";
  }
  return normalized.replace(/\/$/, "");
}
