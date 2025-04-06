from potion import *


class InvisiblePlatform(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Platform")
        self.collisions_enabled = True
        self.width = 8
        self.height = 8
