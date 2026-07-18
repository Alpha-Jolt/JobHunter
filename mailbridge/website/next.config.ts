import type { NextConfig } from 'next'

const config: NextConfig = {
  output: 'standalone',
  pageExtensions: ['ts', 'tsx', 'mdx'],
  experimental: {
    mdxRs: false
  }
}

export default config
