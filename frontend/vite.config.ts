import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";

const rootDir = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  base: "/app/",
  build: {
    outDir: resolve(rootDir, "../static/app"),
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:3333",
      "/auth": "http://127.0.0.1:3333",
      "/echo": "http://127.0.0.1:3333",
    },
  },
});
