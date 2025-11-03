import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx,html,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0ea5e9",
          dark: "#020617",
          accent: "#6366f1",
          magenta: "#db2777",
        },
      },
      fontFamily: {
        heading: ["Cairo", "sans-serif"],
        body: ["Cairo", "sans-serif"],
      },
      backgroundImage: {
        "grid-glow": "radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.25), transparent 60%), radial-gradient(circle at 80% 0%, rgba(99, 102, 241, 0.18), transparent 55%)",
      },
      animation: {
        "pulse-soft": "pulse-soft 3s infinite",
      },
      keyframes: {
        "pulse-soft": {
          "0%, 100%": { opacity: 0.7 },
          "50%": { opacity: 1 },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate"), require("@tailwindcss/forms")],
} satisfies Config;

