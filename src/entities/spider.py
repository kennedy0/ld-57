from potion import *


class Spider(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.x_direction = 1
        self.delay = 0
