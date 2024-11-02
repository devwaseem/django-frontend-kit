import sys
from pathlib import Path
from typing import Generic, Iterable, NamedTuple, TypeVar

from django.http import HttpResponse
from django.template import loader

from frontend_kit import utils
from frontend_kit.manifest import ViteAssetResolver

Props = TypeVar("Props", bound=NamedTuple)


class Page(Generic[Props]):
    JS_FILES: Iterable[str] = []
    CSS_FILES: Iterable[str] = []

    def __init__(self, props: Props) -> None:
        self.props = props

    def get_index_template_path(self) -> str:
        current_file = self.__get_file_path()
        file_path = Path(current_file).parent / "index.html"
        return str(file_path)

    def get_js_file(self) -> str | None:
        current_file = self.__get_file_path()
        dir_path = Path(current_file).parent
        js_file_path = dir_path / "index.js"
        ts_file_path = dir_path / "index.ts"
        if js_file_path.exists():
            return str(js_file_path)
        if ts_file_path.exists():
            return str(ts_file_path)
        return None

    def get_js_manifest_name(self) -> str | None:
        frontend_dir = utils.get_frontend_dir_from_settings()
        if js_file := self.get_js_file():
            js_file = js_file.replace(str(Path(frontend_dir).parent), "")
            if js_file.startswith("/"):
                js_file = js_file[1:]
            return js_file
        return None

    def imports(self) -> str:
        if name := self.get_js_manifest_name():
            return ViteAssetResolver.get_html_tags(file=name)
        return ""

    def render(self) -> str:
        template = loader.get_template(self.get_index_template_path())
        return template.render(
            {
                "page": self,
                "props": self.props,
            }
        )

    def as_response(self) -> HttpResponse:
        return HttpResponse(self.render().encode())

    def __get_file_path(self) -> str:
        current_file = sys.modules[self.__module__].__file__
        if not current_file:
            raise RuntimeError("Could not find current file from modules")
        return current_file
