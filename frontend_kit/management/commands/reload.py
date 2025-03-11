from typing import Any

from django.core.cache import cache
from django.core.management.base import BaseCommand

from frontend_kit.keys import CACHE_KEY_VITE_MANIFEST


class Command(BaseCommand):
    help = "Reload Frontend Kit"

    def handle(self, *args: Any, **options: Any) -> None:  # noqa
        cache.delete(CACHE_KEY_VITE_MANIFEST)
        self.stdout.write(self.style.SUCCESS("Frontend Kit reloaded"))
