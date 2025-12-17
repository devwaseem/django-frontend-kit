from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Generator, cast

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext, loader
from render_block import render_block_to_string

from frontend_kit import utils
from frontend_kit.manifest import (
    AssetTag,
    ModulePreloadTag,
    ModuleTag,
    StyleSheetTag,
    ViteAssetResolver,
)


class FileNotLoadedFromViteError(Exception):
    def __init__(self, file_name: str) -> None:
        super().__init__(f"{file_name} was not included in Vite manifest")


class PageMeta(type):
    def __init__(  # noqa: C901
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
            for file_name in files:
                try:
                    tags_generator = cls.resolve_import(file_name=file_name)  # type: ignore
                except FileNotFoundError:
                    # ignore if any file is not found
                    continue
                for tag in tags_generator:
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

    @classmethod
    def get_template_name(cls) -> str:
        return cls.get_relative_template_name("index.html")

    @classmethod
    def get_relative_template_name(cls, name: str) -> str:
        return str(cls._get_base_path() / name)

    def get_context(self) -> dict[str, Any]:
        return {"page": self}

    def render(self, *, request: HttpRequest) -> str:
        template_name = self.get_template_name()
        return str(
            loader.get_template(template_name=template_name).render(
                context=self.get_context(),
                request=request,
            )
        )

    def render_block(self, *, block_name: str, request: HttpRequest) -> str:
        template_name = self.get_template_name()
        context = RequestContext(request, self.get_context())
        return cast(
            str,
            render_block_to_string(
                template_name=template_name,
                block_name=block_name,
                context=context,
                request=request,
            ),
        )

    def as_response(
        self,
        *,
        request: HttpRequest,
        block_name: str = "",
    ) -> HttpResponse:
        if block_name:
            html = self.render_block(request=request, block_name=block_name)
        else:
            html = self.render(request=request)
        return HttpResponse(content=html.encode())

    @classmethod
    def resolve_import(
        cls, *, file_name: str
    ) -> Generator[AssetTag, None, None]:
        base = cls._get_base_path()
        path = base / file_name if isinstance(file_name, str) else file_name
        if not path.exists():
            raise FileNotFoundError(f"file {file_name} not found")
        if name := cls._get_js_manifest_name(path):
            return ViteAssetResolver.get_imports(file=name)
        raise FileNotLoadedFromViteError(file_name=file_name)

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
