from potion import *


class PlayerDeathFx(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.pausable = False
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "player_death_fx")
        self.sprite.pivot.set_center()
        self.sprite.get_animation("default").loop = False
        self.sprite.play("default")

    def update(self) -> None:
        self.sprite.update()
        if not self.sprite.is_playing:
            self.destroy()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())