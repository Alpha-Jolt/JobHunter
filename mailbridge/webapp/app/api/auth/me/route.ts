import { NextRequest, NextResponse } from 'next/server'
import { jwtDecode } from 'jwt-decode'
import type { AuthUser } from '@/lib/types/api'

interface JwtPayload {
  user_id: string
  workspace_id: string
  tier: string
  role: string
  email?: string
  exp: number
}

export async function GET(req: NextRequest) {
  const token = req.cookies.get('mb_token')?.value
  if (!token) {
    return NextResponse.json({ success: false, error: { code: 'NO_TOKEN', message: 'Not authenticated' } }, { status: 401 })
  }

  try {
    const payload = jwtDecode<JwtPayload>(token)

    // Check expiry
    if (payload.exp * 1000 < Date.now()) {
      return NextResponse.json({ success: false, error: { code: 'TOKEN_EXPIRED', message: 'Token expired' } }, { status: 401 })
    }

    const user: AuthUser = {
      user_id: payload.user_id,
      workspace_id: payload.workspace_id,
      tier: payload.tier as AuthUser['tier'],
      role: payload.role as AuthUser['role'],
      email: payload.email ?? ''
    }

    return NextResponse.json({ success: true, user })
  } catch {
    return NextResponse.json({ success: false, error: { code: 'INVALID_TOKEN', message: 'Invalid token' } }, { status: 401 })
  }
}
