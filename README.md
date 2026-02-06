# Django Frontend Kit

[![PyPI](https://img.shields.io/pypi/v/django-frontend-kit.svg)](https://pypi.org/project/django-frontend-kit/)
[![Python](https://img.shields.io/pypi/pyversions/django-frontend-kit.svg)](https://pypi.org/project/django-frontend-kit/)
[![Django](https://img.shields.io/badge/Django-4.2%2B%20%28incl%206.0%29-0C4B33)](https://www.djangoproject.com/)
[![License](https://img.shields.io/pypi/l/django-frontend-kit.svg)](LICENSE)

An opinionated way to structure and ship modern frontend assets in Django using Vite. It provides:

- A `manage.py scaffold` command to bootstrap a `frontend/` workspace.
- Template tags for injecting Vite assets (dev server in `DEBUG`, manifest in production).
- A lightweight “Page” abstraction that keeps templates, JS/CSS entrypoints, and views aligned.

## Why this exists

Most Django + Vite integrations solve “include the scripts”. Django Frontend Kit also nudges you into a consistent project layout:

- `frontend/layouts/...` for shared shells (base template + base JS/CSS).
- `frontend/pages/...` for page-level templates and entrypoints.
- Optional “custom entries” for React/Vue/Alpine widgets without adopting a full SPA.

## Features

- Vite dev server in development (`DEBUG=True`) with automatic `@vite/client` injection.
- Production asset resolution via Vite `manifest.json` + Django `static()` URLs.
- Modulepreload + stylesheet tags generated from the manifest (better performance by default).
- Scaffolding for a working `frontend/` structure and a `vite.config.js`.

## Requirements

- Python `>= 3.9`
- Django `>= 4.2` (including 6.0)
- Node.js + npm/pnpm/yarn (for Vite)

## Installation

```bash
pip install django-frontend-kit
```

Alternative installers:

```bash
uv add django-frontend-kit
```

```bash
poetry add django-frontend-kit
```

## Quickstart

### 1) Add the app

`settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "frontend_kit",
]
```

### 2) Scaffold the frontend workspace

From the same directory as `manage.py`:

```bash
python manage.py scaffold
```

This creates:

- `frontend/` (templates + entrypoints + Python modules)
- `vite.config.js` (configured for this kit)

### 3) Install JS dependencies

```bash
npm init -y
npm install --save-dev vite @iamwaseem99/vite-plugin-django-frontend-kit
```

Add scripts to `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
```

### 4) Configure Django settings

At minimum:

```python
DJFK_FRONTEND_DIR = BASE_DIR / "frontend"
VITE_OUTPUT_DIR = BASE_DIR / "dist"
VITE_DEV_SERVER_URL = "http://localhost:5173/"
DJFK_DEV_ENV = True

TEMPLATES = [
    {
        # ...
        "DIRS": [DJFK_FRONTEND_DIR],
    }
]

STATICFILES_DIRS = [VITE_OUTPUT_DIR]
```

Notes:

- `DJFK_FRONTEND_DIR` must exist on disk (the scaffold command creates it).
- `VITE_OUTPUT_DIR` must match your Vite `build.outDir` (see `vite.config.js`).
- `DJFK_DEV_ENV` controls dev behavior. When `True`, assets are served from the Vite dev server; when `False`, assets are resolved from the manifest.

### 5) Run in development

In two terminals:

```bash
npm run dev
```

```bash
python manage.py runserver
```

## How it works

- When `DJFK_DEV_ENV=True`, asset tags point to the Vite dev server and HMR works as usual.
- When `DJFK_DEV_ENV=False`, Django Frontend Kit reads `VITE_OUTPUT_DIR/.vite/manifest.json` and emits:
  - `<link rel="modulepreload" ...>` for imported chunks
  - `<link rel="stylesheet" ...>` for CSS
  - `<script type="module" ...></script>` for the entry module

### CSP nonce behavior (dev only)

If `DJFK_DEV_ENV=True` and `request.csp_nonce` is available in the template context, Django Frontend Kit (Django 6+ compatible) adds a `nonce` attribute to:

- `<script type="module">`
- `<link rel="stylesheet">`

No nonce is added when `DJFK_DEV_ENV=False` (production/manifest mode), and `modulepreload` tags never receive a nonce.

## Project layout

After scaffolding, you’ll have a structure like:

```text
frontend/
  layouts/
    base/
      __init__.py
      index.html
      entry.head.ts   # optional, loaded in <head>
      entry.ts        # loaded at end of <body>
      main.css
  pages/
    home/
      __init__.py
      index.html
      entry.ts
```

Important: `frontend/` is a Python package. Keep `__init__.py` files so Django can import your `Page` classes.

## Creating pages and layouts

### Layouts (`frontend/layouts/...`)

Layouts are just `Page` subclasses. By convention they define shared HTML + shared entrypoints.

`frontend/layouts/base/__init__.py`:

```python
from frontend_kit.page import Page

class BaseLayout(Page): ...
```

`frontend/layouts/base/index.html` (scaffolded):

```django
{% load fk_tags %}
<!doctype html>
<html>
  <head>
    {% fk_preloads %}
    {% fk_stylesheets %}
    {% fk_head_scripts %}
  </head>
  <body>
    {% block body %}{% endblock %}
    {% fk_body_scripts %}
  </body>
</html>
```

### Pages (`frontend/pages/...`)

`frontend/pages/home/__init__.py`:

```python
from frontend.layouts.base import BaseLayout

class HomePage(BaseLayout):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
```

`frontend/pages/home/index.html`:

```django
{% extends "layouts/base/index.html" %}
{% block body %}
  <h1>Hello {{ page.name }}</h1>
{% endblock %}
```

And in a view:

```python
from django.http import HttpRequest, HttpResponse
from django.views import View
from frontend.pages.home import HomePage

class HomeView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return HomePage(name="User").as_response(request=request)
```

## Template tags

Load tags with `{% load fk_tags %}`. All tags expect a `page` object in template context (the `Page` base class provides it).

- `{% fk_preloads %}`: modulepreload links (production only)
- `{% fk_stylesheets %}`: CSS links
- `{% fk_head_scripts %}`: `<script type="module">` tags intended for `<head>`
- `{% fk_body_scripts %}`: `<script type="module">` tags intended for end of `<body>`
- `{% fk_custom_entry "name" %}`: loads `name.entry.ts`/`name.entry.js` relative to the current page directory

## Guides

### Tailwind CSS

The included example project uses **Tailwind v4** via the official Vite plugin.

1. Install dependencies:
   ```bash
   npm install --save-dev tailwindcss @tailwindcss/vite
   ```
2. Add Tailwind to `vite.config.js` (before `DjangoFrontendKit()`):
   ```js
   import tailwindcss from "@tailwindcss/vite";

   export default defineConfig({
     plugins: [tailwindcss(), DjangoFrontendKit()],
   });
   ```
3. Add a Tailwind config (example `tailwind.config.cjs`):
   ```js
   export default {
     content: ["./frontend/**/*.{html,js,ts,jsx,tsx,vue,py}"],
     theme: { extend: {} },
     plugins: [],
   };
   ```
4. Import Tailwind in your base CSS (scaffolded `frontend/layouts/base/main.css`):
   ```css
   @import "tailwindcss";
   ```
5. Ensure the CSS is imported by a Vite entrypoint that’s loaded on your pages (scaffolded `frontend/layouts/base/entry.head.ts` is a good place):
   ```ts
   import "./main.css";
   ```

### React (widgets / islands)

1. Install dependencies:
   ```bash
   npm install react react-dom
   npm install --save-dev @vitejs/plugin-react
   ```
2. Enable the React plugin in `vite.config.js`:
   ```js
   import react from "@vitejs/plugin-react";

   export default defineConfig({
     plugins: [react(), DjangoFrontendKit()],
   });
   ```
3. Create a custom entry file in a page directory (must end with `.entry.js` or `.entry.ts` so it’s included in the manifest):
   - `frontend/pages/home/react.entry.js`:
     ```js
     import React from "react";
     import { createRoot } from "react-dom/client";

     function App() {
       return <div>Hello from React</div>;
     }

     const el = document.getElementById("react-app");
     if (el) createRoot(el).render(<App />);
     ```
4. Add a mount point + include the entry in your template:
   ```django
   <div id="react-app"></div>
   {% fk_custom_entry "react" %}
   ```

### Vue (widgets / islands)

1. Install dependencies:
   ```bash
   npm install vue
   npm install --save-dev @vitejs/plugin-vue
   ```
2. Enable the Vue plugin in `vite.config.js`:
   ```js
   import vue from "@vitejs/plugin-vue";

   export default defineConfig({
     plugins: [vue(), DjangoFrontendKit()],
   });
   ```
3. Create a Vue component + an entry file (entry must end with `.entry.js` or `.entry.ts`):
   - `frontend/pages/home/HelloVue.vue`:
     ```vue
     <template>
       <div>Hello from Vue</div>
     </template>
     ```
   - `frontend/pages/home/vue.entry.ts`:
     ```ts
     import { createApp } from "vue";
     import HelloVue from "./HelloVue.vue";

     const el = document.getElementById("vue-app");
     if (el) createApp(HelloVue).mount(el);
     ```
4. Add a mount point + include the entry in your template:
   ```django
   <div id="vue-app"></div>
   {% fk_custom_entry "vue" %}
   ```

### Notes about entrypoints

The Vite plugin bundled with this project only treats these files as build inputs:

- `entry.js` / `entry.ts`
- `entry.head.js` / `entry.head.ts`
- `*.entry.js` / `*.entry.ts`

So keep “entry” files as `.js`/`.ts` (they can import `.jsx`, `.tsx`, `.vue`, CSS, etc.).

## Production checklist

1. Build assets:
   ```bash
   npm run build
   ```
2. Ensure `DEBUG=False`.
3. Ensure Django can serve static assets in production (e.g. WhiteNoise, CDN, or your platform’s static hosting).
4. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

If you use WhiteNoise, consider `CompressedManifestStaticFilesStorage` so hashed assets are served efficiently.

## Troubleshooting

- `DJFK_FRONTEND_DIR is not set / does not exist`: set it in `settings.py` and run `python manage.py scaffold`.
- `VITE_OUTPUT_DIR is not set / does not exist`: set it in `settings.py` and ensure it matches your Vite build output directory.
- `manifest.json` not found: run `npm run build` and verify `VITE_OUTPUT_DIR/.vite/manifest.json` exists.
- `...was not included in Vite manifest`: ensure the file is part of Vite build inputs (entrypoints must be reachable/declared).

## Example project

This repo includes a working example in `example/` showing:

- A base layout (`frontend/layouts/base/`) with `entry.head.ts` and `entry.ts`
- A page (`frontend/pages/home/`) that renders Django template HTML and mounts optional JS widgets

## Versioning & stability

This project is currently in **Beta**. Expect occasional breaking changes until `1.0.0`.

## Contributing

- Run linting: `ruff check .`
- Run type checking: `mypy .`

PRs are welcome. If you’re proposing a behavior change, include a short rationale and an example project diff.

## License

MIT — see [LICENSE](LICENSE).
