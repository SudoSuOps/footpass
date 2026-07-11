import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Production build is served as static files by nginx behind Caddy.
// The dev proxy lets `npm run dev` talk to the API published on :8000.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      "/api": "http://localhost:8000",
      "/camera": "http://localhost:8001",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
