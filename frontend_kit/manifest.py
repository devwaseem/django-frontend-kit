from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generator, Hashable, NamedTuple, Self, cast

from django.core.cache import cache
import orjson
from django.conf import settings
from django.templatetags.static import static

from frontend_kit.keys import CACHE_KEY_VITE_MANIFEST



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
            raise FileNotFoundError(f"File {file} does not exist in manifest, did you build your Vite project?")
        entry = self.entries[file]
        for js_file in entry.import_list:
            yield ModulePreloadTag(src=static(self.entries[js_file].file))
        yield from self.__get_stylesheets(entry=entry)
        yield ModuleTag(src=static(entry.file))

    def __get_stylesheets(self, entry: ManifestEntry) -> Generator[StyleSheetTag, None, None]:
        stylesheets_html: list[StyleSheetTag] = []
        for css_file in entry.css_list:
            css_static_url = static(css_file)
            yield StyleSheetTag(src=css_static_url)
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
            if cache.has_key(CACHE_KEY_VITE_MANIFEST): 
                manifest_data = cast(dict[str, ManifestEntry], cache.get(CACHE_KEY_VITE_MANIFEST))
            else:
                manifest_data = get_vite_manifest()
                cache.set(CACHE_KEY_VITE_MANIFEST, manifest_data, 60 * 60 * 24 * 1000)
        
            resolver = ManifestAssetResolver(manifest_data)
        yield from resolver.get_imports(file=file)

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


def _get_manifest_data() -> str:
    output_dir = settings.VITE_OUTPUT_DIR
    manifest_path = Path(output_dir) / ".vite" / "manifest.json"

    with manifest_path.open("r") as manifest_fd:
        return manifest_fd.read()
