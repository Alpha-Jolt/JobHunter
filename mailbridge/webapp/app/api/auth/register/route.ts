import { NextRequest, NextResponse } from 'next/server'
import { registerBackend } from '@/lib/api/auth'

const MAX_AGE = 60 * 60 * 24

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const result = await registerBackend(body)

    const res = NextResponse.json({ success: true, user_id: result.user_id, workspace_id: result.workspace_id })

    res.cookies.set('mb_token', result.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
      maxAge: MAX_AGE
    })

    return res
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Registration failed'
    const code = (err as { code?: string }).code ?? 'REGISTER_FAILED'
    const status = code === 'EMAIL_EXISTS' ? 409 : 400
    return NextResponse.json({ success: false, error: { code, message } }, { status })
  }
}
