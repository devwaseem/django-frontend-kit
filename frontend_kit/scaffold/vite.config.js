import { glob } from "glob";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import VitePluginDjangoFrontendKit from "@iamwaseem99/vite-plugin-django-frontend-kit";

export default defineConfig(async ({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  const isDevelopment = mode == "development";
  const outputDir = env.VITE_APP_OUTPUT_DIR || "./dist";
  return {
    root: ".",
    resolve: {
      alias: {
        "@": path.resolve("./frontend"),
        "@pages": path.resolve("./frontend/pages"),
        "@shared": path.resolve("./frontend/shared"),
        "@layouts": path.resolve("./frontend/layouts"),
      },
    },
    plugins: [
      VitePluginDjangoFrontendKit({
        frontendDirs: ["./frontend"],
        glob_pattern: "/**/*.{js,ts}",
      }),
    ],
    build: {
      ssr: false,
      outDir: outputDir,
      manifest: true,
      emptyOutDir: true,
      sourcemap: isDevelopment ? "inline" : false,
      minify: isDevelopment ? false : "esbuild",
    },
  };
});
