import Link from 'next/link'
import { Zap } from 'lucide-react'

export function Footer() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--bg)]">
      <div className="mx-auto max-w-6xl px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8">
        <div className="col-span-2 md:col-span-1">
          <Link href="/" className="flex items-center gap-2 mb-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent">
              <Zap className="h-4 w-4 text-white" />
            </div>
            <span className="font-semibold text-[var(--text)]">Mail-Bridge</span>
          </Link>
          <p className="text-sm text-[var(--text-muted)]">Multi-tenant email delivery platform.</p>
        </div>

        {[
          { title: 'Product', links: [{ href: '/pricing', label: 'Pricing' }, { href: '/docs', label: 'Docs' }] },
          { title: 'Developers', links: [{ href: '/docs/quickstart', label: 'Quickstart' }, { href: '/docs/api-reference', label: 'API Reference' }] },
          { title: 'Company', links: [{ href: '#', label: 'About' }, { href: '#', label: 'Contact' }] }
        ].map(col => (
          <div key={col.title}>
            <p className="text-sm font-medium text-[var(--text)] mb-3">{col.title}</p>
            <ul className="space-y-2">
              {col.links.map(l => (
                <li key={l.href}><Link href={l.href} className="text-sm text-[var(--text-muted)] hover:text-[var(--text)] transition-colors">{l.label}</Link></li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-[var(--border)] px-6 py-4 text-center text-xs text-[var(--text-muted)]">
        © {new Date().getFullYear()} Mail-Bridge. All rights reserved.
      </div>
    </footer>
  )
}
