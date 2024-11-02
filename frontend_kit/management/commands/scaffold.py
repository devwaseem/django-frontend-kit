import shutil
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Setup Django Frontend"

    def handle(self, *args: Any, **options: Any) -> None:  # noqa
        scaffold_dir = Path(__file__).parent.parent.parent / "scaffold"
        frontend_dir = Path(settings.BASE_DIR) / "frontend"
        if frontend_dir.exists():
            raise CommandError("Frontend directory already exists")

        vite_config_destination = Path.cwd() / "vite.config.js"
        if vite_config_destination.exists():
            raise CommandError(
                "vite.config.js already exists, "
                "you need to remove it to continue..."
            )

        self.stdout.write("Creating frontend directory...")

        scaffold_frontend_dir = str(scaffold_dir / "frontend")
        shutil.copytree(scaffold_frontend_dir, frontend_dir)
        self.stdout.write(self.style.SUCCESS("Frontend directory created"))

        scaffold_vite_config = scaffold_dir / "vite.config.js"
        shutil.copy(scaffold_vite_config, Path.cwd())
        self.stdout.write(self.style.SUCCESS("vite.config.js created"))

        self.stdout.write(
            self.style.SUCCESS(
                'Add `BASE_DIR / "frontend"` to template DIRS in settings.py'
            )
        )
