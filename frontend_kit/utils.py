from pathlib import Path

from django.conf import settings


def get_frontend_dir_from_settings() -> Path:
    frontend_dir: str = getattr(settings, "DJFK_FRONTEND_DIR", "")
    if not frontend_dir:
        raise RuntimeError(
            "DJFK_FRONTEND_DIR is not set in settings.py, please set it to the "
            "output directory of your Vite build"
        )
    frontend_dir_path = Path(frontend_dir)
    if not frontend_dir_path.exists():
        raise RuntimeError(
            f"{frontend_dir} does not exist, "
            "please check DJFK_FRONTEND_DIR settings to ensure you "
            "pass correct dir"
        )

    if not frontend_dir_path.is_dir():
        raise RuntimeError(f"{frontend_dir} is not an directory")
    return frontend_dir_path
