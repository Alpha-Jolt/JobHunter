'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Zap } from 'lucide-react'
import { withBasePath } from '@/lib/base-path'
import { useAuthStore } from '@/lib/store/authStore'
import { getMe } from '@/lib/api/auth'

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters')
})
type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const router = useRouter()
  const setUser = useAuthStore(s => s.setUser)
  const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema)
  })

  async function onSubmit(data: FormData) {
    const res = await fetch(withBasePath('/api/auth/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    })
    if (!res.ok) {
      const body = await res.json()
      setError('root', { message: body.error?.message ?? 'Login failed' })
      return
    }
    const user = await getMe()
    setUser(user)
    router.push('/')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg)] px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 mb-8 justify-center">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-semibold text-[var(--text)]">Mail-Bridge</span>
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 shadow-base">
          <h1 className="text-xl font-semibold text-[var(--text)] mb-1">Welcome back</h1>
          <p className="text-sm text-[var(--text-muted)] mb-6">Sign in to your workspace</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Email</label>
              <input
                {...register('email')}
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-colors"
              />
              {errors.email && <p className="mt-1 text-xs text-error">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Password</label>
              <input
                {...register('password')}
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-colors"
              />
              {errors.password && <p className="mt-1 text-xs text-error">{errors.password.message}</p>}
            </div>

            {errors.root && (
              <p className="rounded-lg bg-error/10 px-3 py-2 text-sm text-error">{errors.root.message}</p>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-lg bg-accent py-2.5 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-[var(--text-muted)]">
            No account?{' '}
            <Link href="/register" className="text-accent hover:underline">Create workspace</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
