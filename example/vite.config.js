import { glob } from "glob";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import tailwindcss from "tailwindcss";

async function buildRollupInput(frontendDirs) {
  let rollupInput = {};
  for (let dir of frontendDirs) {
    dir = path.resolve(dir);
    for (let subDir of ["pages", "shared", "layout"]) {
      let subDirPath = dir + "/" + subDir;
      let resolved_files = await glob(subDirPath + "/**/*.{js,ts}");
      for (let file of resolved_files) {
        let key = path.resolve(file).replace(dir, "");
        if (key.startsWith("/")) {
          key = key.slice(1);
        }
        key = key.replace(/(index)?\.(js|ts|css)$/g, "");
        key = key.replace(/\//g, "-");
        if (key.endsWith("-")) {
          key = key.slice(0, -1);
        }
        rollupInput[key] = file;
      }
    }
  }
  return rollupInput;
}

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
    css: {
      postcss: {
        plugins: [tailwindcss()],
      },
    },
    build: {
      ssr: false,
      outDir: outputDir,
      manifest: true,
      emptyOutDir: true,
      sourcemap: isDevelopment ? "inline" : false,
      minify: isDevelopment ? false : "esbuild",
      rollupOptions: {
        input: await buildRollupInput(["./frontend"]),
      },
    },
  };
});
