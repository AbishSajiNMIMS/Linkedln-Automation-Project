import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        muted: "hsl(var(--muted))",
        panel: "hsl(var(--panel))",
        accent: "hsl(var(--accent))",
        signal: "hsl(var(--signal))"
      },
      boxShadow: {
        soft: "0 18px 60px rgba(16, 24, 40, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
