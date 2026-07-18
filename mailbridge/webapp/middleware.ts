import { NextRequest, NextResponse } from 'next/server'
import { jwtDecode } from 'jwt-decode'

interface JwtPayload {
  user_id: string
  workspace_id: string
  role: string
  exp: number
}

// Routes only accessible by 'owner' role
const OWNER_ONLY = ['/credentials', '/webhooks', '/admin']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  const token = req.cookies.get('mb_token')?.value

  // Allow auth pages without token
  if (pathname.startsWith('/login') || pathname.startsWith('/register')) {
    if (token) return NextResponse.redirect(new URL('/', req.url))
    return NextResponse.next()
  }

  // Allow API routes to handle their own auth
  if (pathname.startsWith('/api/')) return NextResponse.next()

  // Require token for all other routes
  if (!token) {
    return NextResponse.redirect(new URL(`/login?from=${encodeURIComponent(pathname)}`, req.url))
  }

  try {
    const payload = jwtDecode<JwtPayload>(token)

    // Check expiry
    if (payload.exp * 1000 < Date.now()) {
      const res = NextResponse.redirect(new URL('/login', req.url))
      res.cookies.set('mb_token', '', { httpOnly: true, path: '/', maxAge: 0 })
      return res
    }

    // RBAC: owner-only routes
    const isOwnerRoute = OWNER_ONLY.some(r => pathname.startsWith(r))
    if (isOwnerRoute && payload.role !== 'owner') {
      return NextResponse.redirect(new URL('/', req.url))
    }

    return NextResponse.next()
  } catch {
    const res = NextResponse.redirect(new URL('/login', req.url))
    res.cookies.set('mb_token', '', { httpOnly: true, path: '/', maxAge: 0 })
    return res
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|public/).*)']
}
