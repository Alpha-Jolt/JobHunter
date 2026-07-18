import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Providers } from '@/components/Providers'
import { BASE_PATH } from '@/lib/base-path'
import './globals.css'

export const metadata: Metadata = {
  title: 'Mail-Bridge',
  description: 'Multi-tenant email delivery platform',
  icons: {
    icon: `${BASE_PATH || ''}/logo.png`,
    apple: `${BASE_PATH || ''}/logo.png`,
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning
      className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
