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
          DEFAULT: '#006D5B', // Deeper, more premium emerald green
          hover: '#005445',
          soft: '#E0F2EF',
          glow: '#00836f33'
        },
        accent: {
          DEFAULT: '#E65C00', // Richer, burnt orange
          hover: '#C24D00',
          soft: '#FFF0E5',
        },
        secondary: {
          DEFAULT: '#1E293B',
        },
        success: '#059669',
        warning: '#D97706',
        error: '#DC2626',
        background: {
          DEFAULT: '#F4F7FA',
          card: '#FFFFFF',
          muted: '#E2E8F0',
        },
        border: '#CBD5E1',
        text: {
          primary: '#0F172A',
          secondary: '#475569',
        }
      },
      fontFamily: {
        sans: ['"Outfit"', 'sans-serif'],
        display: ['"Bricolage Grotesque"', 'sans-serif'],
      },
      borderRadius: {
        card: '16px',
      },
      boxShadow: {
        card: '0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 0 3px 0px rgba(0,0,0,0.02)',
        glow: '0 0 20px -5px var(--tw-shadow-color)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
