'use client'

import dynamic from 'next/dynamic'

export const HeroDynamic = dynamic(
  () => import('./Hero').then(m => m.Hero),
  { ssr: false }
)
