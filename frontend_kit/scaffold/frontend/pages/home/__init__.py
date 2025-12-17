import random

from frontend.layouts.base import BaseLayout


class HomePage(BaseLayout):
    def __init__(self) -> None:
        super().__init__(title="Home")

    def lucky_number(self) -> int:
        return random.randint(1, 100)
