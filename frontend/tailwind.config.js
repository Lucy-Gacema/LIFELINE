/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eefdf4",
          100: "#d6f9e2",
          200: "#aef0c8",
          300: "#78e2a8",
          400: "#42cd85",
          500: "#1eb26a",
          600: "#128f54",
          700: "#107346",
          800: "#125c3a",
          900: "#104b31",
        },
      },
      fontSize: {
        "tap-lg": ["1.5rem", { lineHeight: "2rem" }],
      },
      minHeight: {
        touch: "3.5rem",
      },
    },
  },
  plugins: [],
};
