from potion import *


class Enemy(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Enemy")
        self.hp = 0
        self.max_hp = 0
        self.start_position = Point.zero()

    def awake(self) -> None:
        self.start_position = self.position()

    def damage(self) -> None:
        self.hp -= 1
        if self.hp <= 0:
            self.on_death()
            self.active = False

    def on_activate(self) -> None:
        self.hp = self.max_hp
        self.on_spawn()
        self.set_position(self.start_position)

    def on_spawn(self) -> None:
        pass

    def on_death(self) -> None:
        pass
