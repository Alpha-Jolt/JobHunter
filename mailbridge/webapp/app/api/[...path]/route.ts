import { NextRequest, NextResponse } from 'next/server'

const GATEWAY = process.env.API_GATEWAY_URL ?? 'http://localhost:3009'

async function proxy(req: NextRequest): Promise<NextResponse> {
  const token = req.cookies.get('mb_token')?.value
  if (!token) {
    return NextResponse.json(
      { success: false, error: { code: 'NO_TOKEN', message: 'Not authenticated' } },
      { status: 401 }
    )
  }

  const { pathname, search } = new URL(req.url)
  const upstream = `${GATEWAY}${pathname}${search}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-Requested-With': 'XMLHttpRequest',
  }

  const body = req.method !== 'GET' && req.method !== 'HEAD'
    ? await req.text()
    : undefined

  const res = await fetch(upstream, {
    method: req.method,
    headers,
    body,
  })

  const data = await res.text()
  return new NextResponse(data, {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  })
}

export const GET = proxy
export const POST = proxy
export const PUT = proxy
export const DELETE = proxy
export const PATCH = proxy
