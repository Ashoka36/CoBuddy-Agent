import { jsxLocPlugin } from "@builder.io/vite-plugin-jsx-loc";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "path";
import { defineConfig } from "vite";

// Conditionally import Manus plugin only in development
let vitePluginManusRuntime;
try {
  vitePluginManusRuntime = (await import("vite-plugin-manus-runtime")).vitePluginManusRuntime;
} catch {
  // Plugin not available outside Manus environment
  vitePluginManusRuntime = () => ({ name: 'dummy-manus-plugin' });
}

const isManusEnvironment = process.env.MANUS_ENVIRONMENT === 'true' || process.env.NODE_ENV === 'development';
const plugins = [react(), tailwindcss(), jsxLocPlugin()];

if (isManusEnvironment && vitePluginManusRuntime) {
  plugins.push(vitePluginManusRuntime());
}

export default defineConfig({
  plugins,
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets"),
    },
  },
  envDir: path.resolve(import.meta.dirname),
  root: path.resolve(import.meta.dirname, "client"),
  publicDir: path.resolve(import.meta.dirname, "client", "public"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
  },
  define: {
    // Provide fallback values for environment variables
    VITE_ANALYTICS_ENDPOINT: process.env.VITE_ANALYTICS_ENDPOINT || '""',
    VITE_ANALYTICS_WEBSITE_ID: process.env.VITE_ANALYTICS_WEBSITE_ID || '""',
    VITE_NVIDIA_NIM_ENDPOINT: process.env.VITE_NVIDIA_NIM_ENDPOINT || '"https://integrate.api.nvidia.com/v1/chat/completions"',
    MANUS_ENVIRONMENT: isManusEnvironment ? 'true' : 'false'
  },
  optimizeDeps: {
    exclude: ['vite-plugin-manus-runtime']
  },
  server: {
    host: true,
    allowedHosts: [
      "localhost",
      "127.0.0.1",
      "0.0.0.0",
      // Manus-specific hosts only in Manus environment
      ...(isManusEnvironment ? [
        ".manuspre.computer",
        ".manus.computer", 
        ".manus-asia.computer",
        ".manuscomputer.ai",
        ".manusvm.computer"
      ] : [])
    ],
    fs: {
      strict: true,
      deny: ["**/.*"],
    },
  },
});
