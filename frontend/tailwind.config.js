/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        border: "#e5e7eb",
        background: "#f8fafc",
        foreground: "#0f172a",
        muted: "#f1f5f9",
        primary: "#2563eb",
        "primary-foreground": "#ffffff"
      },
      borderRadius: { xl: "0.875rem", "2xl": "1rem" }
    }
  },
  plugins: [],
};
