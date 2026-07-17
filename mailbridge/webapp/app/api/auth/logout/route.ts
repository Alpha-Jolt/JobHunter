import { NextRequest, NextResponse } from 'next/server'
import { logoutBackend } from '@/lib/api/auth'

export async function POST(req: NextRequest) {
  const token = req.cookies.get('mb_token')?.value

  if (token) {
    try { await logoutBackend(token) } catch { /* ignore — clear cookie regardless */ }
  }

  const res = NextResponse.json({ success: true })
  res.cookies.set('mb_token', '', { httpOnly: true, path: '/', maxAge: 0 })
  return res
}
