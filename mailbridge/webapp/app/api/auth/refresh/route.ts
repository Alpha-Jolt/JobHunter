import { NextRequest, NextResponse } from 'next/server'
import { refreshBackend } from '@/lib/api/auth'

const MAX_AGE = 60 * 60 * 24

export async function POST(req: NextRequest) {
  const token = req.cookies.get('mb_token')?.value
  if (!token) {
    return NextResponse.json({ success: false, error: { code: 'NO_TOKEN', message: 'Not authenticated' } }, { status: 401 })
  }

  try {
    const result = await refreshBackend(token)
    const res = NextResponse.json({ success: true })
    res.cookies.set('mb_token', result.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
      maxAge: MAX_AGE
    })
    return res
  } catch {
    const res = NextResponse.json({ success: false, error: { code: 'REFRESH_FAILED', message: 'Token refresh failed' } }, { status: 401 })
    res.cookies.set('mb_token', '', { httpOnly: true, path: '/', maxAge: 0 })
    return res
  }
}
