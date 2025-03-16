import sys
from functools import cached_property
from pathlib import Path
from typing import Generator, Generic, Iterable, NamedTuple, TypeVar, cast

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

Props = TypeVar("Props", bound=NamedTuple)


class Page(Generic[Props]):
    """
    Page class for linking JS Files and Django.

    This class is used to define the page structure and imports.
    It is responsible for importing the necessary JavaScript and CSS files
    for the page.
    """

    stylesheets: list[StyleSheetTag]
    preload_imports: list[ModulePreloadTag]
    head_imports: list[ModuleTag]
    pre_body_imports: list[ModuleTag]
    post_body_imports: list[ModuleTag]

    head_js_files: Iterable[str] = [
        "index.js",
        "index.ts",
    ]
    pre_body_js_files: Iterable[str | Path] = [
        "index.pre.body.js",
        "index.pre.body.ts",
    ]
    post_body_js_files: Iterable[str | Path] = [
        "index.post.body.js",
        "index.post.body.ts",
    ]

    def __init__(self, props: Props) -> None:
        self.props = props
        self.stylesheets = []
        self.preload_imports = []
        self.head_imports = []
        self.pre_body_imports = []
        self.post_body_imports = []

        self.__setup_imports()

    @cached_property
    def _base_path(self) -> Path:
        return Path(self.__get_file_path()).parent

    def __get_js_manifest_name(self, file_path: Path) -> str | None:
        frontend_dir = utils.get_frontend_dir_from_settings()
        if not file_path.exists():
            return None
        return str(file_path.relative_to(Path(frontend_dir).parent)).lstrip(
            "/"
        )

    def __setup_imports(self) -> None:
        imported_modules = set()
        if settings.DEBUG:
            self.head_imports.append(
                ModuleTag(src=f"{settings.VITE_DEV_SERVER_URL}@vite/client")
            )

        files_imports_list = (
            (self.head_js_files, self.head_imports),
            (self.pre_body_js_files, self.pre_body_imports),
            (self.post_body_js_files, self.post_body_imports),
        )

        for files, imports in files_imports_list:
            for import_tag in self.__get_imports(files=files):
                if import_tag in imported_modules:
                    continue

                if isinstance(import_tag, ModulePreloadTag):
                    self.preload_imports.append(import_tag)
                elif isinstance(import_tag, StyleSheetTag):
                    self.stylesheets.append(import_tag)
                elif isinstance(import_tag, ModuleTag):
                    imports.append(import_tag)
                imported_modules.add(import_tag)

    def get_imports(
        self, files: Iterable[str | Path]
    ) -> Generator[AssetTag, None, None]:
        yield from self.__get_imports(
            files=files, ignore_not_found_files=False
        )

    def __get_imports(
        self,
        *,
        files: Iterable[str | Path],
        ignore_not_found_files: bool = True,
    ) -> Generator[AssetTag, None, None]:
        for file in files:
            file_path = (
                self._base_path / file if isinstance(file, str) else file
            )
            if not file_path.exists() and not ignore_not_found_files:
                raise FileNotFoundError(f"File {file_path} does not exist")
            if name := self.__get_js_manifest_name(file_path=file_path):
                yield from ViteAssetResolver.get_imports(file=name)

    def render(self, *, request: HttpRequest) -> str:
        template = loader.get_template(str(self._base_path / "index.html"))
        return cast(
            str,
            template.render(
                {
                    "page": self,
                    "props": self.props,
                },
                request=request,
            ),
        )

    def as_response(self, *, request: HttpRequest) -> HttpResponse:
        return HttpResponse(self.render(request=request).encode())

    def __get_file_path(self) -> str:
        if current_file := sys.modules[self.__module__].__file__:
            return current_file
        raise RuntimeError("Could not find current file from modules")
