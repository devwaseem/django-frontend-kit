import type { Plugin } from "vite";

export interface DjangoFrontendKitOptions {
  frontendDirs?: string[];
}

export default function DjangoFrontendKit(
  options?: DjangoFrontendKitOptions
): Plugin;
