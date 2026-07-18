'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, Mail, FileText, Key, Webhook,
  Users, Settings, Inbox
} from 'lucide-react'
import Image from 'next/image'
import { cn } from '@/lib/utils/cn'
import { useAuth } from '@/lib/hooks/useAuth'
import { useAuthStore } from '@/lib/store/authStore'
import { withBasePath } from '@/lib/base-path'

const NAV = [
  { href: '/',             label: 'Dashboard',    icon: LayoutDashboard, ownerOnly: false },
  { href: '/emails',       label: 'Emails',       icon: Mail,            ownerOnly: false },
  { href: '/incoming-logs',label: 'Incoming',     icon: Inbox,           ownerOnly: false },
  { href: '/templates',    label: 'Templates',    icon: FileText,        ownerOnly: false },
  { href: '/credentials',  label: 'Credentials',  icon: Key,             ownerOnly: true  },
  { href: '/webhooks',     label: 'Webhooks',     icon: Webhook,         ownerOnly: true  },
  { href: '/admin',        label: 'Team',         icon: Users,           ownerOnly: true  },
  { href: '/settings',     label: 'Settings',     icon: Settings,        ownerOnly: false }
]

export function Sidebar() {
  const pathname = usePathname()
  const { user } = useAuth()
  const setUser = useAuthStore(s => s.setUser)
  const [isUpgrading, setIsUpgrading] = useState(false)
  const isOwner = user?.role === 'owner'

  async function handleUpgrade() {
    try {
      setIsUpgrading(true)
      const res = await fetch(withBasePath('/api/auth/upgrade'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data?.error?.message ?? 'Failed to upgrade')
      }
      setUser(data.user)
      alert('Workspace upgraded to Pro successfully!')
    } catch (err: any) {
      alert(err.message || 'Upgrade failed')
    } finally {
      setIsUpgrading(false)
    }
  }

  const links = NAV.filter(n => !n.ownerOnly || isOwner)

  return (
    <aside className="fixed left-0 top-0 h-full w-56 border-r border-[var(--border)] bg-[var(--bg)] flex flex-col z-20">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-[var(--border)]">
        <Image src="/logo.png" alt="Mail-Bridge" width={28} height={28} className="rounded-lg" />
        <span className="font-semibold tracking-tight text-[var(--text)]">Mail-Bridge</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {links.map(({ href, label, icon: Icon }) => {
          const active = href === '/' ? pathname === '/' : pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                active
                  ? 'bg-accent/10 text-accent border-l-2 border-accent font-medium'
                  : 'text-[var(--text-muted)] hover:bg-[var(--surface)] hover:text-[var(--text)]'
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* User */}
      {user && (
        <div className="px-4 py-4 border-t border-[var(--border)]">
          <p className="text-xs text-[var(--text-muted)] truncate">{user.email}</p>
          <p className="text-xs text-accent capitalize mt-0.5">{user.role} · {user.tier}</p>
          {user.role === 'owner' && user.tier === 'free' && (
            <button
              onClick={handleUpgrade}
              disabled={isUpgrading}
              className="mt-3 w-full flex items-center justify-center gap-2 rounded-lg bg-accent px-3 py-1.5 text-xs font-semibold text-white hover:bg-accent-hover disabled:opacity-50 transition-colors shadow-sm"
            >
              {isUpgrading ? 'Upgrading...' : 'Upgrade to Pro'}
            </button>
          )}
        </div>
      )}
    </aside>
  )
}
