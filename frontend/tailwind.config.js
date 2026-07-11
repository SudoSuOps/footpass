/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Calm OpenFootLab / Freddy palette (self-hosted, no external anything)
        ink: "#1b2a4a", // navy
        brand: "#2e6fb0", // blue
        accent: "#d64545", // red (used sparingly)
        sand: "#f4efe6", // warm background
        card: "#ffffff",
        muted: "#5b6b82",
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};
