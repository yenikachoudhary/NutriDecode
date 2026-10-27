/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          cream: '#F8F6F0',
          creamCard: '#EFECE5',
          creamHover: '#E8E4DC',
          sage: '#E2E6DF',
          sageDark: '#CBD3C6',
          rust: '#A8472A',
          rustHover: '#933B20',
          forest: '#3D4F40',
          forestDark: '#2C3A2F',
          mustard: '#F2B731',
          charcoal: '#221F1D',
          muted: '#67625B',
          borderSage: '#D1D7CD'
        }
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
