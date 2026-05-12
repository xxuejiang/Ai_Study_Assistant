import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");
const configPath = path.resolve(projectRoot, "project.config.json");
const projectConfig = JSON.parse(fs.readFileSync(configPath, "utf-8"));

const backendHost = projectConfig.backend?.host || "127.0.0.1";
const backendPort = projectConfig.backend?.port || 8000;
const apiPrefix = projectConfig.backend?.apiPrefix || "/api";
const frontendHost = projectConfig.frontend?.host || "127.0.0.1";
const frontendPort = projectConfig.frontend?.port || 5173;
const previewPort = projectConfig.frontend?.previewPort || 4173;

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: frontendHost,
    port: frontendPort,
    strictPort: true,
  },
  preview: {
    host: frontendHost,
    port: previewPort,
    strictPort: true,
  },
  define: {
    __APP_CONFIG__: JSON.stringify({
      apiBaseUrl: `http://${backendHost}:${backendPort}${apiPrefix}`,
    }),
  },
});
