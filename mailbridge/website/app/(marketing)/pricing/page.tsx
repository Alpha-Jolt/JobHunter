import type { Metadata } from 'next'
import Link from 'next/link'
import { Check } from 'lucide-react'

export const metadata: Metadata = { title: 'Pricing' }

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    desc: 'For personal projects and testing',
    features: ['500 emails/month', '1 credential', '5 templates', 'Email logs (7 days)', 'Community support'],
    cta: 'Get started',
    href: 'http://localhost:3010/register',
    highlight: false
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    desc: 'For growing teams and applications',
    features: ['50,000 emails/month', '10 credentials', 'Unlimited templates', 'Email logs (90 days)', 'Webhooks', 'Priority support'],
    cta: 'Start Pro',
    href: 'http://localhost:3010/register',
    highlight: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    desc: 'For large-scale deployments',
    features: ['Unlimited emails', 'Unlimited credentials', 'Full RBAC', 'Email logs (1 year)', 'SLA guarantee', 'Dedicated support'],
    cta: 'Contact us',
    href: 'mailto:hello@mail-bridge.dev',
    highlight: false
  }
]

export default function PricingPage() {
  return (
    <div className="py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center mb-14">
          <h1 className="text-4xl font-bold text-[var(--text)] mb-3">Simple pricing</h1>
          <p className="text-[var(--text-muted)]">Start free. Scale as you grow.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLANS.map(p => (
            <div key={p.name} className={`rounded-2xl border p-8 flex flex-col ${p.highlight ? 'border-accent bg-accent/5 ring-1 ring-accent/30' : 'border-[var(--border)] bg-[var(--surface)]'}`}>
              {p.highlight && (
                <span className="inline-flex self-start rounded-full bg-accent px-3 py-0.5 text-xs font-medium text-white mb-4">Most popular</span>
              )}
              <h2 className="text-xl font-bold text-[var(--text)]">{p.name}</h2>
              <div className="mt-2 mb-1">
                <span className="text-3xl font-bold text-[var(--text)]">{p.price}</span>
                <span className="text-sm text-[var(--text-muted)]">{p.period}</span>
              </div>
              <p className="text-sm text-[var(--text-muted)] mb-6">{p.desc}</p>
              <ul className="space-y-3 mb-8 flex-1">
                {p.features.map(f => (
                  <li key={f} className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                    <Check className="h-4 w-4 text-accent shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link href={p.href} className={`rounded-xl py-2.5 text-center text-sm font-medium transition-colors ${p.highlight ? 'bg-accent text-white hover:bg-[#4f46e5]' : 'border border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--bg)]'}`}>
                {p.cta}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
