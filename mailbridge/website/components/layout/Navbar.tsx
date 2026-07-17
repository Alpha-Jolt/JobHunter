'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import Image from 'next/image'
import { useState } from 'react'
import { ThemeToggle } from './ThemeToggle'

const NAV = [
  { href: '/', label: 'Home' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/docs', label: 'Docs' }
]

export function Navbar() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--bg)]/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <Image src="/logo.png" alt="Mail-Bridge" width={28} height={28} className="rounded-lg" />
          <span className="font-semibold text-[var(--text)]">Mail-Bridge</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {NAV.map(n => (
            <Link key={n.href} href={n.href} className={`text-sm transition-colors ${pathname === n.href ? 'text-[var(--text)] font-medium' : 'text-[var(--text-muted)] hover:text-[var(--text)]'}`}>
              {n.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <ThemeToggle />
          <Link href="http://localhost:3010/login" className="rounded-lg border border-[var(--border)] px-4 py-1.5 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors">Sign in</Link>
          <Link href="http://localhost:3010/register" className="rounded-lg bg-accent px-4 py-1.5 text-sm text-white hover:bg-[#4f46e5] transition-colors">Get started</Link>
        </div>

        <button className="md:hidden text-[var(--text-muted)]" onClick={() => setOpen(v => !v)}>
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-[var(--border)] bg-[var(--bg)] px-6 py-4 space-y-3">
          {NAV.map(n => (
            <Link key={n.href} href={n.href} onClick={() => setOpen(false)} className="block text-sm text-[var(--text-muted)] hover:text-[var(--text)]">{n.label}</Link>
          ))}
          <div className="pt-2 flex gap-3">
            <Link href="http://localhost:3010/login" className="rounded-lg border border-[var(--border)] px-4 py-1.5 text-sm text-[var(--text-muted)]">Sign in</Link>
            <Link href="http://localhost:3010/register" className="rounded-lg bg-accent px-4 py-1.5 text-sm text-white">Get started</Link>
          </div>
        </div>
      )}
    </header>
  )
}
