import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        royal: ['Georgia', '"Times New Roman"', 'serif'],
      },
      colors: {
        // Royal navy-tinted slate (dark surfaces) + ivory (light surfaces)
        slate: {
          50: "#faf8f2",
          100: "#f2eee1",
          200: "#e5dfca",
          300: "#cbd2e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#2a3560",
          800: "#1a2347",
          900: "#111a3a",
          950: "#0a1030",
        },
        // Royal blue replaces default blue everywhere
        blue: {
          50: "#eef3ff",
          100: "#dde7ff",
          200: "#bccfff",
          300: "#8fadf5",
          400: "#5f82e6",
          500: "#3d5fcf",
          600: "#2c47b0",
          700: "#22388f",
          800: "#1b2d70",
          900: "#14214f",
          950: "#0c1535",
        },
        gold: {
          50: "#fffaeb",
          100: "#fdf0c4",
          200: "#fbe08a",
          300: "#f5c542",
          400: "#e6b422",
          500: "#d4af37",
          600: "#b8891a",
          700: "#8f6712",
        },
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          50: "#f0f7ff",
          100: "#e0effe",
          500: "#2563eb",
          600: "#1d4ed8",
          700: "#1e40af",
          900: "#1e3a8a",
        },
        risk: {
          low: "#10b981",
          medium: "#f59e0b",
          high: "#ef4444",
        }
      },
    },
  },
  plugins: [],
};
export default config;
