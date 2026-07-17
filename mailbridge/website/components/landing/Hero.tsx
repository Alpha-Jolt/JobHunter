'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'

export function Hero() {
  return (
    <section className="relative overflow-hidden py-24 md:py-36">
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-accent/10 blur-3xl" />
      </div>

      <div className="mx-auto max-w-4xl px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-flex items-center rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-medium text-accent mb-6">
            Multi-tenant · Multi-provider · Production-ready
          </span>
          <h1 className="text-4xl md:text-6xl font-bold text-[var(--text)] leading-tight mb-6">
            Email delivery,<br />
            <span className="text-accent">built for scale</span>
          </h1>
          <p className="text-lg text-[var(--text-muted)] max-w-2xl mx-auto mb-10">
            Send transactional emails via Gmail, Outlook, or SMTP. Template with Handlebars, track delivery, receive webhooks — all from one platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="http://localhost:3010/register" className="rounded-xl bg-accent px-8 py-3 text-sm font-medium text-white hover:bg-[#4f46e5] transition-colors">
              Start for free
            </Link>
            <Link href="/docs/quickstart" className="rounded-xl border border-[var(--border)] px-8 py-3 text-sm font-medium text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors">
              Read the docs
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
