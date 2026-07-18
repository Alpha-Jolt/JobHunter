'use client'

import { useRouter } from 'next/navigation'
import { LogOut } from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'
import { useAuthStore } from '@/lib/store/authStore'

export function Topbar() {
  const router = useRouter()
  const clear = useAuthStore(s => s.clear)

  async function handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    clear()
    router.push('/login')
  }

  return (
    <header className="fixed top-0 left-56 right-0 h-14 border-b border-[var(--border)] bg-[var(--bg)]/80 backdrop-blur-sm flex items-center justify-end px-6 gap-3 z-10">
      <ThemeToggle />
      <button
        onClick={handleLogout}
        className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] hover:text-[var(--text)] transition-colors"
      >
        <LogOut className="h-4 w-4" />
        Logout
      </button>
    </header>
  )
}
