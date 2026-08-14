import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// host: true so the dev server is reachable from a browser outside the
// container. /api is proxied to the FastAPI backend, which keeps the browser
// on a single origin and avoids CORS entirely in development.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.BACKEND_URL ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
