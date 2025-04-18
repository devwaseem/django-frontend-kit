import json
from abc import ABC, abstractmethod
from functools import cache
from pathlib import Path
from typing import Any, Generator, Hashable, NamedTuple, Self, cast

from django.conf import settings
from django.templatetags.static import static


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


class AssetTag(ABC, Hashable):
    src: str

    def __init__(self, src: str) -> None:
        self.src: str = src

    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.src)

    def __eq__(self, value: object) -> bool:
        return self.src == cast(Self, value).src

    def __str__(self) -> str:
        return self.src

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(src={self.src!r})"


class ModulePreloadTag(AssetTag):
    def render(self) -> str:
        return f'<link rel="modulepreload" href="{self.src}" />'


class ModuleTag(AssetTag):
    def render(self) -> str:
        return f'<script type="module" src="{self.src}"></script>'


class StyleSheetTag(AssetTag):
    def render(self) -> str:
        return f'<link rel="stylesheet" href="{self.src}">'


class AssetResolver(ABC):
    @abstractmethod
    def get_imports(self, file: str) -> Generator[AssetTag, None, None]: ...


class ViteDevServerAssetResolver(AssetResolver):
    def get_imports(self, file: str) -> Generator[AssetTag, None, None]:
        vite_dev_server_url = getattr(
            settings, "VITE_DEV_SERVER_URL", "http://localhost:5173/"
        )
        static_url = vite_dev_server_url + file
        yield ModuleTag(src=static_url)


class ManifestAssetResolver(AssetResolver):
    def __init__(self, entries: dict[str, ManifestEntry]) -> None:
        self.entries = entries

    def get_imports(self, file: str) -> Generator[AssetTag, None, None]:
        if file not in self.entries:
            raise FileNotFoundError(
                f"File {file} does not exist in manifest, "
                "did you build your Vite project?"
            )
        entry = self.entries[file]
        for js_file in entry.import_list:
            yield ModulePreloadTag(src=static(self.entries[js_file].file))
        yield from self.__get_stylesheets(entry=entry)
        yield ModuleTag(src=static(entry.file))

    def __get_stylesheets(
        self, entry: ManifestEntry
    ) -> Generator[StyleSheetTag, None, None]:
        for css_file in entry.css_list:
            yield StyleSheetTag(src=static(css_file))

        for imported_entry in entry.import_list:
            yield from self.__get_stylesheets(
                entry=self.entries[imported_entry]
            )


class ViteAssetResolver:
    @staticmethod
    def get_imports(file: str) -> Generator[AssetTag, None, None]:
        resolver: AssetResolver
        if settings.DEBUG:
            resolver = ViteDevServerAssetResolver()
        else:
            resolver = ManifestAssetResolver(get_vite_manifest())
        yield from resolver.get_imports(file=file)


@cache
def get_vite_manifest() -> dict[str, ManifestEntry]:
    entries: dict[str, ManifestEntry] = {}
    if not hasattr(settings, "VITE_OUTPUT_DIR"):
        raise RuntimeError(
            "VITE_OUTPUT_DIR is not set in settings.py, please set it to the "
            "output directory of your Vite build"
        )

    vite_output_dir = Path(settings.VITE_OUTPUT_DIR)
    if not vite_output_dir.exists():
        raise RuntimeError(
            f"{settings.VITE_OUTPUT_DIR} does not exist, "
            "please check VITE_OUTPUT_DIR settings to ensure you "
            "pass correct dir"
        )

    manifest_path = vite_output_dir / ".vite" / "manifest.json"
    manifest_content = manifest_path.read_text()
    manifest: dict[str, Any] = json.loads(manifest_content)
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
