from typing import NamedTuple

from frontend_kit.page import Page


class HomePageProps(NamedTuple): ...


class HomePage(Page[HomePageProps]): 
    def __init__(self, props: HomePageProps) -> None:
        super().__init__(props)
        self.react_imports = self.get_imports(files=[
            "react.jsx"
        ])
