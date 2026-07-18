import { NextRequest, NextResponse } from 'next/server'
import { loginBackend } from '@/lib/api/auth'
import { ApiError } from '@/lib/api/client'
import { BASE_PATH } from '@/lib/base-path'

const MAX_AGE = 60 * 60 * 24 // 24h

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const result = await loginBackend(body)

    const res = NextResponse.json({ success: true })

    res.cookies.set('mb_token', result.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: BASE_PATH || '/',
      maxAge: MAX_AGE,
    })

    return res
  } catch (err: unknown) {
    const message =
      err instanceof ApiError
        ? err.message
        : err instanceof Error
          ? err.message
          : 'Login failed'
    const code = err instanceof ApiError ? err.code : 'LOGIN_FAILED'
    const status = err instanceof ApiError ? err.status : 401
    return NextResponse.json({ success: false, error: { code, message } }, { status })
  }
}
