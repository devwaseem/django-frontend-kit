# vite-plugin-django-frontend-kit

A Vite plugin to generate rollup input for django frontend kit

## Installation

```bash
npm install @iamwaseem99/vite-plugin-django-frontend-kit
```

## Usage

```js
import { defineConfig } from "vite";
import VitePluginDjangoFrontendKit from "vite-plugin-django-frontend-kit";

export default defineConfig({
  plugins: [
    DjangoFrontendKit(),
  ],
});
```

## Options

```js
VitePluginDjangoFrontendKit({
  frontendDirs: ["./frontend"],
});
```
