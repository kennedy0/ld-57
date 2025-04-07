from potion import *

from entities.enemy import Enemy
from entities.score_fx import ScoreFx


class Goomba(Enemy):
    def __init__(self) -> None:
        super().__init__()

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "goomba")
        self.sprite.play("Walk")
        self.sprite.flip_horizontal = True

        self.collisions_enabled = True
        self.width = 10
        self.height = 9

        self.dx = -.2

        self.sfx = SoundEffect("sfx/enemydeath.wav")

    def on_spawn(self) -> None:
        self.dx = -.2
        self.sprite.play("Walk")
        self.sprite.flip_horizontal = True

    def on_death(self) -> None:
        fx = ScoreFx.instantiate()
        fx.set_position(self.position())
        self.sfx.play()

    def wall_rect(self) -> Rect:
        if self.dx > 0:
            return Rect(self.bbox().right(), self.bbox().top(), 2, 2)
        else:
            return Rect(self.bbox().left() - 2, self.bbox().top(), 2, 2)

    def update(self) -> None:
        self.sprite.update()

        if self.dx <= 0:
            self.sprite.flip_horizontal = True
        else:
            self.sprite.flip_horizontal = False

        self.move_x(self.dx)

        for entity in self.scene.entities.active_entities():
            if entity.solid:
                if entity.intersects(self.wall_rect()):
                    self.dx *= -1
                    break

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() - Point(1, 1))
