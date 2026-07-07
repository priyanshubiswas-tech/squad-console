/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0e14",
        panel: "#121826",
        card: "#171f30",
        cardHover: "#1c2740",
        pitch: "#22c55e",
        indigo: "#6366f1",
        danger: "#ef4444",
        lock: "#facc15",
        textPrimary: "#e5e7eb",
        textSecondary: "#9ca3af",
      },
      borderRadius: {
        card: "12px",
      },
    },
  },
  plugins: [],
};
