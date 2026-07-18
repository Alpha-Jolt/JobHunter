import Link from 'next/link'

export function CTA() {
  return (
    <section className="py-20 bg-[var(--surface)]">
      <div className="mx-auto max-w-2xl px-6 text-center">
        <h2 className="text-3xl font-bold text-[var(--text)] mb-4">Ready to send?</h2>
        <p className="text-[var(--text-muted)] mb-8">Free tier includes 500 emails/month. No credit card required.</p>
        <Link href="http://localhost:3010/register" className="inline-flex rounded-xl bg-accent px-8 py-3 text-sm font-medium text-white hover:bg-[#4f46e5] transition-colors">
          Create free workspace
        </Link>
      </div>
    </section>
  )
}
