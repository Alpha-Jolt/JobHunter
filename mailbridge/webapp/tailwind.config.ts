import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme
        dark: {
          bg:      '#0f0f0f',
          surface: '#1a1a1a',
          border:  '#2a2a2a',
          muted:   '#404040',
          text:    '#f5f5f5',
          'text-muted': '#a0a0a0'
        },
        // Light theme
        light: {
          bg:      '#fafafa',
          surface: '#ffffff',
          border:  '#e5e5e5',
          muted:   '#d4d4d4',
          text:    '#0f0f0f',
          'text-muted': '#737373'
        },
        accent: {
          DEFAULT: '#6366f1',
          hover:   '#4f46e5',
          light:   '#818cf8'
        },
        success: '#22c55e',
        warning: '#f59e0b',
        error:   '#ef4444'
      },
      fontFamily: {
        sans: ['var(--font-geist-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-geist-mono)', 'monospace']
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.25rem'
      },
      boxShadow: {
        sm:  '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
        md:  '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)',
        'dark-sm': '0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)',
        'dark-md': '0 4px 6px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.4)'
      }
    }
  },
  plugins: []
}

export default config
