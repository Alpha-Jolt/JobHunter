const STEPS = [
  { n: '01', title: 'Add a credential', desc: 'Connect Gmail via OAuth, Outlook via OAuth, or any SMTP server. Credentials are encrypted at rest.' },
  { n: '02', title: 'Create a template', desc: 'Write your email HTML with Handlebars variables. Preview with live data before saving.' },
  { n: '03', title: 'Send via API', desc: 'POST to /api/emails/send with your credential ID, template ID, and variable values.' },
  { n: '04', title: 'Track delivery', desc: 'Monitor status in the dashboard or receive real-time events via webhooks.' }
]

export function HowItWorks() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-4xl px-6">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-[var(--text)] mb-3">How it works</h2>
          <p className="text-[var(--text-muted)]">Up and running in minutes</p>
        </div>
        <div className="space-y-6">
          {STEPS.map(s => (
            <div key={s.n} className="flex gap-6 items-start">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent/10 text-sm font-bold text-accent">{s.n}</div>
              <div>
                <h3 className="font-semibold text-[var(--text)] mb-1">{s.title}</h3>
                <p className="text-sm text-[var(--text-muted)] leading-relaxed">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
