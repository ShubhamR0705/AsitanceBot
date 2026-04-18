import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      colors: {
        brand: {
          50: "#e9fbf7",
          100: "#c9f4ed",
          500: "#10a691",
          600: "#0b8f7d",
          700: "#087264"
        },
        accent: {
          50: "#fff0f5",
          500: "#e64980",
          600: "#c9366a"
        },
        ink: "#17201f",
        muted: "#66736f",
        line: "#dfe7e3",
        base: "#f7f9f8",
        surface: "#ffffff",
        elevated: "#fbfefd"
      },
      boxShadow: {
        soft: "0 12px 32px rgba(23, 32, 31, 0.08)",
        lift: "0 18px 48px rgba(16, 166, 145, 0.14)"
      }
    }
  },
  plugins: []
} satisfies Config;

