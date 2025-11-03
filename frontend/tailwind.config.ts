import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#050816",
        neon: "#1be7ff",
        magenta: "#ff009e",
        azure: "#00a4ff",
        glass: "rgba(15, 50, 80, 0.45)"
      },
      fontFamily: {
        cairo: ["Cairo", "sans-serif"]
      },
      boxShadow: {
        glow: "0 0 25px rgba(0, 204, 255, 0.45)",
        neon: "0 0 30px rgba(255, 0, 158, 0.35)"
      },
      backgroundImage: {
        grid: "radial-gradient(circle at center, rgba(27, 231, 255, 0.15) 0, transparent 60%)"
      }
    }
  },
  plugins: []
};

export default config;
