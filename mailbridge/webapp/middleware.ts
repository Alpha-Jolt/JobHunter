import { NextRequest, NextResponse } from 'next/server'
import { jwtDecode } from 'jwt-decode'

interface JwtPayload {
  user_id: string
  workspace_id: string
  role: string
  exp: number
}

const BASE = (process.env.NEXT_PUBLIC_BASE_PATH ?? '').replace(/\/$/, '')
const OWNER_ONLY = ['/credentials', '/webhooks', '/admin']

function stripBase(pathname: string): string {
  if (BASE && (pathname === BASE || pathname.startsWith(`${BASE}/`))) {
    const rest = pathname.slice(BASE.length)
    return rest || '/'
  }
  return pathname
}

function redirect(req: NextRequest, path: string): NextResponse {
  // Keep redirects under basePath (new URL('/login', origin) would escape it)
  const target = BASE && path.startsWith('/') ? `${BASE}${path}` : path
  return NextResponse.redirect(new URL(target, req.url))
}

export function middleware(req: NextRequest) {
  const pathname = stripBase(req.nextUrl.pathname)
  const token = req.cookies.get('mb_token')?.value

  if (pathname.startsWith('/login') || pathname.startsWith('/register')) {
    if (token) return redirect(req, '/')
    return NextResponse.next()
  }

  if (pathname.startsWith('/api/')) return NextResponse.next()

  if (!token) {
    return redirect(req, `/login?from=${encodeURIComponent(pathname)}`)
  }

  try {
    const payload = jwtDecode<JwtPayload>(token)

    if (payload.exp * 1000 < Date.now()) {
      const res = redirect(req, '/login')
      res.cookies.set('mb_token', '', {
        httpOnly: true,
        path: BASE || '/',
        maxAge: 0,
      })
      return res
    }

    const isOwnerRoute = OWNER_ONLY.some((r) => pathname.startsWith(r))
    if (isOwnerRoute && payload.role !== 'owner') {
      return redirect(req, '/')
    }

    return NextResponse.next()
  } catch {
    const res = redirect(req, '/login')
    res.cookies.set('mb_token', '', {
      httpOnly: true,
      path: BASE || '/',
      maxAge: 0,
    })
    return res
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|public/).*)'],
}
