from frontend.layouts.base import BaseLayout


class HomePage(BaseLayout):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
