import { Mail, Shield, Zap, Webhook, FileText, Users } from 'lucide-react'

const FEATURES = [
  { icon: Mail, title: 'Multi-provider', desc: 'Gmail OAuth 2.0, Outlook OAuth, and any SMTP server. Switch providers without changing your code.' },
  { icon: Shield, title: 'AES-256 encrypted', desc: 'All credentials stored with AES-256-GCM encryption. Your OAuth tokens and SMTP passwords are never exposed.' },
  { icon: Zap, title: 'Async queue', desc: 'Redis-backed FIFO queue with automatic 3-retry worker loop. Emails never block your application.' },
  { icon: FileText, title: 'Handlebars templates', desc: 'Create reusable templates with variable substitution, versioning, and one-click rollback.' },
  { icon: Webhook, title: 'Webhooks', desc: 'Receive real-time delivery events with HMAC-signed payloads and exponential backoff retry.' },
  { icon: Users, title: 'Multi-tenant', desc: 'Workspace isolation with owner/member roles. Enterprise tier supports full RBAC.' }
]

export function Features() {
  return (
    <section className="py-20 bg-[var(--surface)]">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-[var(--text)] mb-3">Everything you need</h2>
          <p className="text-[var(--text-muted)]">Production-grade email infrastructure without the complexity</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map(f => (
            <div key={f.title} className="rounded-2xl border border-[var(--border)] bg-[var(--bg)] p-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/10 mb-4">
                <f.icon className="h-5 w-5 text-accent" />
              </div>
              <h3 className="font-semibold text-[var(--text)] mb-2">{f.title}</h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
