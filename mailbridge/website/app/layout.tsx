import type { Metadata } from 'next'
import { Providers } from '@/components/layout/Providers'
import './globals.css'

export const metadata: Metadata = {
  title: { default: 'Mail-Bridge', template: '%s | Mail-Bridge' },
  description: 'Multi-tenant email delivery platform. Send, template, and track emails at scale.',
  icons: { icon: '/logo.png', apple: '/logo.png' },
  openGraph: { title: 'Mail-Bridge', description: 'Multi-tenant email delivery platform', type: 'website', images: ['/logo.png'] }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
