from frontend_kit.page import Page


class BaseLayout(Page):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.title = title


__all__ = ["BaseLayout"]
