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
          DEFAULT: '#0F4C81',
          hover: '#0C3D68',
        },
        secondary: {
          DEFAULT: '#2563EB',
        },
        success: '#16A34A',
        warning: '#D97706',
        error: '#DC2626',
        background: {
          DEFAULT: '#F8FAFC',
          card: '#FFFFFF',
          muted: '#F3F4F6',
        },
        border: '#E5E7EB',
        text: {
          primary: '#111827',
          secondary: '#6B7280',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
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
