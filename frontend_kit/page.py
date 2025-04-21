from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Generator, Iterable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.template import loader

from frontend_kit import utils
from frontend_kit.manifest import (
    AssetTag,
    ModulePreloadTag,
    ModuleTag,
    StyleSheetTag,
    ViteAssetResolver,
)


class PageMeta(type):
    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> None:
        super().__init__(name, bases, namespace)

        if cls.__name__ == "Page":
            return  # Skip base

        cls._assets: dict[str, list[AssetTag]] = {
            "stylesheets": [],
            "preloads": [],
            "head": [],
            "body": [],
        }

        # Load files from Meta
        head_files = [
            "entry.head.js",
            "entry.head.ts",
        ]
        body_files = [
            "entry.js",
            "entry.ts",
        ]

        if settings.DEBUG and hasattr(settings, "VITE_DEV_SERVER_URL"):
            cls._assets["head"].append(
                ModuleTag(src=f"{settings.VITE_DEV_SERVER_URL}@vite/client")
            )

        seen: set[AssetTag] = set()
        for files, section in ((head_files, "head"), (body_files, "body")):
            for tag in cls._resolve_imports(files):  # type: ignore
                if tag in seen:
                    continue
                if isinstance(tag, StyleSheetTag):
                    cls._assets["stylesheets"].append(tag)
                elif isinstance(tag, ModulePreloadTag):
                    cls._assets["preloads"].append(tag)
                elif isinstance(tag, ModuleTag):
                    cls._assets[section].append(tag)
                seen.add(tag)


class Page(metaclass=PageMeta):
    _assets: dict[str, list[AssetTag]] = {}

    def __init__(self) -> None:
        self.stylesheets: list[StyleSheetTag] = []
        self.preload_imports: list[ModulePreloadTag] = []
        self.head_imports: list[ModuleTag] = []
        self.body_imports: list[ModuleTag] = []
        self._collect_inherited_assets()

    def _collect_inherited_assets(self) -> None:
        collected: dict[str, list[AssetTag]] = {
            "stylesheets": [],
            "preloads": [],
            "head": [],
            "body": [],
        }
        seen: set[AssetTag] = set()

        for cls in self.__class__.__mro__:
            if not hasattr(cls, "_assets"):
                continue
            for key, values in cls._assets.items():
                for tag in values:
                    if tag not in seen:
                        collected[key].append(tag)
                        seen.add(tag)

        self.stylesheets = collected["stylesheets"]  # type: ignore
        self.preload_imports = collected["preloads"]  # type: ignore
        self.head_imports = collected["head"]  # type: ignore
        self.body_imports = collected["body"]  # type: ignore

    def get_template(self) -> str:
        return loader.get_template(str(self._get_base_path() / "index.html"))

    def render(self, *, request: HttpRequest) -> str:
        template = self.get_template()
        return str(template.render({"page": self}, request=request))

    def as_response(self, *, request: HttpRequest) -> HttpResponse:
        return HttpResponse(self.render(request=request).encode())

    @classmethod
    def _resolve_imports(
        cls, files: Iterable[str | Path]
    ) -> Generator[AssetTag, None, None]:
        base = cls._get_base_path()
        for file in files:
            path = base / file if isinstance(file, str) else file
            if not path.exists():
                continue
            if name := cls._get_js_manifest_name(path):
                yield from ViteAssetResolver.get_imports(file=name)

    @classmethod
    def _get_base_path(cls) -> Path:
        return Path(cls._get_file_path()).parent

    @classmethod
    def _get_file_path(cls) -> str:
        mod = sys.modules[cls.__module__]
        path = getattr(mod, "__file__", None)
        if not path:
            raise RuntimeError(f"Can't determine file path for {cls}")
        return str(path)

    @classmethod
    def _get_js_manifest_name(cls, file_path: Path) -> str | None:
        frontend_dir = utils.get_frontend_dir_from_settings()
        if not file_path.exists():
            return None
        return str(file_path.relative_to(Path(frontend_dir).parent)).lstrip(
            "/"
        )
