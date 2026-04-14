import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          // ─── Light commerce palette ──────────────────────
          bg:      "#F5F5F7",
          white:   "#FFFFFF",
          primary: "#E8315A",
          teal:    "#00B9A0",
          orange:  "#FF7A3C",
          text:    "#1A1A1A",
          muted:   "#6B7280",
          light:   "#AAAAAA",
          border:  "#E5E7EB",
          card:    "#FFFFFF",
          // ─── Legacy aliases (auto-adapts all old components) ──
          black:   "#F5F5F7",
          gold:    "#E8315A",
          cream:   "#1A1A1A",
        },
      },
      fontFamily: {
        serif: ["var(--font-playfair)", "Georgia", "serif"],
        sans:  ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-up": "fadeUp 0.5s ease forwards",
        "fade-in": "fadeIn 0.3s ease forwards",
        shimmer:   "shimmer 1.5s infinite",
        marquee:   "marquee 28s linear infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        marquee: {
          "0%":   { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
