/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        appleBg: '#000000',
        appleCard: 'rgba(28, 28, 30, 0.65)',
        appleBorder: 'rgba(255, 255, 255, 0.08)',
        appleBlue: '#007AFF',
        appleBlueHover: '#0071e3',
        appleGreen: '#30D158',
        appleRed: '#FF453A',
        appleGray: '#8E8E93',
        appleGrayLight: '#AEAEB2',
        appleDarkGray: '#1C1C1E',
        appleDarkerGray: '#2C2C2E',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Display"',
          '"SF Pro Text"',
          '"SF Pro"',
          'system-ui',
          'sans-serif'
        ],
      },
      backdropBlur: {
        '2xl': '40px',
      }
    },
  },
  plugins: [],
}
