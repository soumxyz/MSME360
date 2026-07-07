/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#00836f', // IDBI Teal Green
          hover: '#006a5a',
          soft: '#e6f4f1',
        },
        accent: {
          DEFAULT: '#f5821f', // IDBI Accent Orange
          hover: '#d96d0f',
          soft: '#fef3e7',
        },
        secondary: {
          DEFAULT: '#00836f',
        },
        success: '#047857',
        warning: '#b45309',
        error: '#b91c1c',
        background: {
          DEFAULT: '#f8fafc',
          card: '#ffffff',
          muted: '#f1f5f9',
        },
        border: '#e2e8f0',
        text: {
          primary: '#0f172a',
          secondary: '#64748b',
        }
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      borderRadius: {
        card: '12px',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
      }
    },
  },
  plugins: [],
}
