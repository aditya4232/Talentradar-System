/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        dark: { 900: '#0D0F1A', 800: '#111827', 700: '#1F2937', 600: '#374151' },
        brand: { 500: '#818CF8', 600: '#6366F1', 700: '#4F46E5' },
        teal: { 400: '#2DD4BF', 500: '#14B8A6' },
      },
    },
  },
  plugins: [],
}
