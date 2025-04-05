from potion import *


class Enemy(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Enemy")
        self.hp = 1

    def damage(self) -> None:
        self.hp -= 1
        if self.hp <= 0:
            self.destroy()
            self.on_death()

    def on_death(self) -> None:
        pass
