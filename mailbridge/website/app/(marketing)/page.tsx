import { HeroDynamic } from '@/components/landing/HeroDynamic'
import { Features } from '@/components/landing/Features'
import { HowItWorks } from '@/components/landing/HowItWorks'
import { CTA } from '@/components/landing/CTA'

export default function HomePage() {
  return (
    <>
      <HeroDynamic />
      <Features />
      <HowItWorks />
      <CTA />
    </>
  )
}
