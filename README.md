# Django Frontend Kit

**Django Frontend Kit** is an opinionated frontend scaffolder for Django that integrates seamlessly with ViteJS, offering a streamlined setup for modern frontend tooling within your Django projects.

---


## Installation

Via pip into a virtualenv:

```bash
pip install django-frontend-kit
```

In settings.py add the following:

Add `frontend_kit` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "frontend_kit",
]
```

frontend_kit will look for a `frontend` directory in the setting `DJFK_FRONTEND_DIR`.
It is recommend to put the `frontend` directory in the root of your project.

```python

DJFK_FRONTEND_DIR = BASE_DIR / "frontend"

TEMPLATES = [
        {
            ...
            "DIRS": [DJFK_FRONTEND_DIR],
            ...
        }
]

```

By default, frontend_kit will use vite's dev server for development, and 
will use built assets for production using the generated manifest.json from vite.

Set dev server url:

```python
VITE_DEV_SERVER_URL = "http://localhost:5173/"
```

In production, we need to build the frontend assets, so set the output dir and
add the same to `STATICFILES_DIRS` so django can collect staticfiles:


```python
DJFK_VITE_OUTPUT_DIR = os.environ.get("VITE_OUTPUT_DIR", "./dist")
STATICFILES_DIRS = [DJFK_VITE_OUTPUT_DIR]
```


Finally, run the following command to setup the frontend_kit dirs and required files:

```bash
python manage.py scaffold
```

This will create frontend directory, vite config in the `BASE_DIR`

Run the following command to install necessary packages:

```bash
npm install
```

That's it, you are ready to go!

