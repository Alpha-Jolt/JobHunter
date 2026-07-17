/**
 * Base API client — all calls go through Next.js API routes (server-side)
 * which forward to the Nginx gateway. The browser never calls the gateway directly.
 *
 * On the client: calls /api/* (same-origin Next.js routes)
 * On the server: calls API_GATEWAY_URL directly (server-only env var)
 */

const isServer = typeof window === 'undefined'

// Server-side: use gateway URL directly. Client-side: use Next.js API proxy routes.
function getBase(): string {
  if (isServer) {
    return process.env.API_GATEWAY_URL ?? 'http://localhost:3009'
  }
  return ''  // relative — calls /api/* on same origin
}

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

interface FetchOptions extends RequestInit {
  token?: string  // server-side: pass JWT from cookie
}

async function request<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...init } = options
  const base = getBase()
  const url = `${base}${path}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    ...(init.headers as Record<string, string> ?? {})
  }

  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, {
    ...init,
    headers,
    credentials: isServer ? 'omit' : 'include'
  })

  if (!res.ok) {
    let code = 'UNKNOWN_ERROR'
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      code = body?.error?.code ?? code
      message = body?.error?.message ?? message
    } catch { /* ignore parse error */ }
    throw new ApiError(code, message, res.status)
  }

  return res.json() as Promise<T>
}

export const apiClient = {
  get:    <T>(path: string, opts?: FetchOptions) => request<T>(path, { ...opts, method: 'GET' }),
  post:   <T>(path: string, body?: unknown, opts?: FetchOptions) =>
    request<T>(path, { ...opts, method: 'POST', body: JSON.stringify(body) }),
  put:    <T>(path: string, body?: unknown, opts?: FetchOptions) =>
    request<T>(path, { ...opts, method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string, opts?: FetchOptions) => request<T>(path, { ...opts, method: 'DELETE' })
}
