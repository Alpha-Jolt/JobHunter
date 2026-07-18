/**
 * Subpath hosting on app.myjobhunter.in/mailbridge.
 * Empty string for local root hosting (http://localhost:3010).
 */
export const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH ?? '').replace(/\/$/, '')

/** Prefix a root-absolute path for browser fetch()/window navigations. */
export function withBasePath(path: string): string {
  if (!path.startsWith('/')) return path
  if (!BASE_PATH) return path
  if (path === BASE_PATH || path.startsWith(`${BASE_PATH}/`)) return path
  return `${BASE_PATH}${path}`
}
