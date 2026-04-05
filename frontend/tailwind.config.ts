import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{html,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0f1117',
          secondary: '#1a1d27',
          tertiary: '#242836',
        },
        text: {
          primary: '#e8eaed',
          secondary: '#9aa0b0',
        },
        accent: {
          DEFAULT: '#6c63ff',
          hover: '#7b73ff',
        },
        success: '#34d399',
        warning: '#fbbf24',
        error: '#f87171',
        border: {
          DEFAULT: '#2d3142',
          focus: '#6c63ff',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        mono: ['"Fira Code"', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config
