# Django Frontend Kit

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

**Django Frontend Kit** is an opinionated frontend scaffolder for Django, integrating seamlessly with ViteJS. It provides a streamlined setup for modern frontend tooling within your Django projects, enabling efficient development and production workflows.

---

## 🚀 Features

- 📦 **Seamless ViteJS Integration** – Enables modern frontend tooling in Django.
- ⚡ **Zero Config Development** – Uses Vite’s dev server automatically during development.
- 🔧 **Production-Ready Setup** – Manages static assets via Django’s `collectstatic` mechanism.
- 🛠 **Easy Scaffolding** – One command to generate the required frontend structure.

---

## 📥 Installation

You can install `django-frontend-kit` using your preferred package manager:

### Using `uv`
```bash
uv add django-frontend-kit
```

### Using `Poetry`
```bash
poetry add django-frontend-kit
```

### Using `pip`
```bash
pip install django-frontend-kit
```

---

## 🔧 Configuration

### 1️⃣ Add to Installed Apps

In your `settings.py`, add `django-frontend-kit` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "frontend_kit",
    ...
]
```

### 2️⃣ Define Frontend Directory

By default, `django-frontend-kit` looks for a `frontend` directory specified by `DJFK_FRONTEND_DIR`. It is recommended to place it in the root of your project:

```python
DJFK_FRONTEND_DIR = BASE_DIR / "frontend"
```

### Templating support
For Django template engine to find the frontend files, add `DJFK_FRONTEND_DIR` to TEMPLATES DIRS in `settings.py`:

```python
TEMPLATES = [
    {
        ...
        "DIRS": [
            ...
            DJFK_FRONTEND_DIR
            ...
        ],
        ...
    }
]
```

### 3️⃣ Configure Vite Integration

During development, `django-frontend-kit` will use Vite's dev server. Set the dev server URL:

```python
VITE_DEV_SERVER_URL = "http://localhost:5173/"
```

To collect staticfiles built by Vite, add the `VITE_OUTPUT_DIR` to `STATICFILES_DIRS` in `settings.py`:

```python
VITE_OUTPUT_DIR = os.environ.get("VITE_OUTPUT_DIR", "./dist")
STATICFILES_DIRS = [VITE_OUTPUT_DIR]
```

---

## ⚡ Quick Start

### 1️⃣ Frontend Setup

Run the following command to create the required frontend structure:

```bash
python manage.py scaffold
```

This will generate the `frontend` directory and Vite configuration in `BASE_DIR`.

### 2️⃣ Initialize the Frontend Project

Create a `package.json` file:

```bash
npm init -y
```

Install the necessary dependencies:

```bash
npm install vite @iamwaseem99/vite-plugin-django-frontend-kit
```

### Start Development Server

To start the development server, run:

```bash
npm run dev 
```

### Build for Production

To generate production-ready frontend assets, run:

```bash
npm run build
```

and run the following command to collect static files:

```bash
python manage.py collectstatic  
```

---

## TODO:

### README

- [] Add philosophy.
- [] Explain the project structure.
- [] Add how to add and use layouts, pages, shared files.
- [] Add how to use third party libraries like tailwind, react, alpine, etc.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.