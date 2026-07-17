import Link from 'next/link'
import { getAllDocs } from '@/lib/docs'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  const docs = getAllDocs()

  return (
    <>
      <Navbar />
      <div className="mx-auto max-w-6xl px-6 py-10 flex gap-10">
        <aside className="hidden md:block w-56 shrink-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-3">Documentation</p>
          <nav className="space-y-1">
            {docs.map(d => (
              <Link
                key={d.slug.join('/')}
                href={`/docs/${d.slug.join('/')}`}
                className="block rounded-lg px-3 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] hover:text-[var(--text)] transition-colors"
              >
                {d.title}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="flex-1 min-w-0">{children}</main>
      </div>
      <Footer />
    </>
  )
}
