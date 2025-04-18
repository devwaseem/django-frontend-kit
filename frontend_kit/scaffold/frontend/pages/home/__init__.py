import random

from frontend.layouts.base import BaseLayout


class HomePage(BaseLayout):
    def lucky_number(self) -> int:
        return random.randint(1, 100)
