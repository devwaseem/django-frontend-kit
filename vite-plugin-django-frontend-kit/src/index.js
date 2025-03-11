import { glob } from "glob";
import path from "path";

async function generateRollupInput(frontendDirs, glob_pattern) {
  let rollupInput = {};
  for (let dir of frontendDirs) {
    dir = path.resolve(dir);
    for (let subDir of ["pages", "shared", "layout"]) {
      let subDirPath = path.join(dir, subDir);
      let resolved_files = await glob(subDirPath + glob_pattern);
      for (let file of resolved_files) {
        let key = path
          .resolve(file)
          .replace(dir, "")
          .replace(/^\/|\\/g, "");
        key = key.replace(/(index)?\.(js|ts|css)$/g, "").replace(/\//g, "-");
        if (key.endsWith("-")) key = key.slice(0, -1);
        rollupInput[key] = file;
      }
    }
  }
  return rollupInput;
}

export default function VitePluginDjangoFrontendKit(
  options = {
    frontendDirs: ["./frontend"],
    glob_pattern: "/**/*.{js,ts}",
  }
) {
  return {
    name: "vite-plugin-django-frontend-kit",
    enforce: "pre",
    async configResolved(config) {
      config.build.rollupOptions.input = await generateRollupInput(
        options.frontendDirs,
        options.glob_pattern
      );
    },
  };
}
