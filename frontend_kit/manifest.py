import functools
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, NamedTuple

import orjson
from django.conf import settings
from django.templatetags.static import static
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from frontend_kit import utils


class ManifestEntry(NamedTuple):
    name: str
    file: str
    src: str = ""
    is_entry: bool = False
    is_dynamic_entry: bool = False
    import_list: list[str] = []
    asset_list: list[str] = []
    css_list: list[str] = []


class AssetNotFoundError(Exception): ...


class AssetResolver(ABC):
    @abstractmethod
    def get_html_tags(self, file: str) -> str: ...


class ViteDevServerAssetResolver(AssetResolver):
    def get_html_tags(self, file: str) -> str:
        vite_dev_server_url = getattr(
            settings, "VITE_DEV_SERVER_URL", "http://localhost:5173/"
        )
        static_url = vite_dev_server_url + file
        return f"<script type='module' src='{static_url}'></script>"


class ManifestAssetResolver(AssetResolver):
    def __init__(self, entries: dict[str, ManifestEntry]) -> None:
        self.entries = entries

    def get_html_tags(self, file: str) -> str:
        entry = self.entries[file]
        imports_html = self.__get_stylesheets_html(entry=entry)

        for js_file in entry.import_list:
            entry = self.entries[js_file]
            js_static_url = static(entry.file)
            imports_html += (
                f'<link rel="modulepreload" href="{js_static_url}" />'
            )

        imports_html += (
            f'<script type="module" src="{static(entry.file)}"></script>'
        )

        return imports_html

    def __get_stylesheets_html(self, entry: ManifestEntry) -> str:
        stylesheets_html = ""
        for css_file in entry.css_list:
            css_static_url = static(css_file)
            stylesheets_html += (
                f'<link rel="stylesheet" href="{css_static_url}">\n'
            )
        for imported_entry in entry.import_list:
            stylesheets_html += self.__get_stylesheets_html(
                entry=self.entries[imported_entry]
            )
        return stylesheets_html


class ViteAssetResolver:
    @staticmethod
    def get_html_tags(file: str) -> str:
        resolver: AssetResolver
        if settings.DEBUG:
            resolver = ViteDevServerAssetResolver()
        else:
            resolver = ManifestAssetResolver(get_vite_manifest())
        return resolver.get_html_tags(file=file)


@functools.cache
def get_vite_manifest() -> dict[str, ManifestEntry]:
    entries: dict[str, ManifestEntry] = {}
    manifest_content = _get_manifest_data()
    manifest: dict[str, Any] = orjson.loads(manifest_content)
    for file, entry in manifest.items():
        entries[file] = ManifestEntry(
            name=entry["name"],
            file=entry["file"],
            src=entry.get("src", ""),
            is_entry=entry.get("isEntry", False),
            is_dynamic_entry=entry.get("isDynamicEntry", False),
            import_list=entry.get("imports", []),
            asset_list=entry.get("assets", []),
            css_list=entry.get("css", []),
        )

    return entries


@retry(  # type: ignore
    retry=retry_if_exception_type(FileNotFoundError),
    wait=wait_fixed(1),
    stop=stop_after_attempt(10),
    reraise=True,
)
def _get_manifest_data() -> str:
    output_dir = utils.get_frontend_dir_from_settings()
    manifest_path = Path(output_dir) / ".vite" / "manifest.json"

    with manifest_path.open("r") as manifest_fd:
        return manifest_fd.read()
