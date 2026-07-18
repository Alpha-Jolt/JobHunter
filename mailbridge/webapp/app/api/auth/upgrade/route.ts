import { NextRequest, NextResponse } from 'next/server'
import { upgradeBackend } from '@/lib/api/auth'
import { jwtDecode } from 'jwt-decode'
import type { AuthUser } from '@/lib/types/api'

const MAX_AGE = 60 * 60 * 24 // 24h

interface JwtPayload {
  user_id: string
  workspace_id: string
  tier: string
  role: string
  email?: string
  exp: number
}

export async function POST(req: NextRequest) {
  try {
    const token = req.cookies.get('mb_token')?.value
    if (!token) {
      return NextResponse.json(
        { success: false, error: { code: 'UNAUTHORIZED', message: 'Not authenticated' } },
        { status: 401 }
      )
    }

    const result = await upgradeBackend(token)

    // Decode the new token to return the updated user object
    const payload = jwtDecode<JwtPayload>(result.token)
    const user: AuthUser = {
      user_id: payload.user_id,
      workspace_id: payload.workspace_id,
      tier: payload.tier as AuthUser['tier'],
      role: payload.role as AuthUser['role'],
      email: payload.email ?? ''
    }

    const res = NextResponse.json({ success: true, user })

    res.cookies.set('mb_token', result.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
      maxAge: MAX_AGE
    })

    return res
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Upgrade failed'
    const code = (err as { code?: string }).code ?? 'UPGRADE_FAILED'
    return NextResponse.json({ success: false, error: { code, message } }, { status: 400 })
  }
}
