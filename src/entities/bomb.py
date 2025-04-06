from potion import *

from entities.explosion_fx import ExplosionFx


class Bomb(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Bomb")

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "bomb")
        self.sprite.play("Slow")

        self.collisions_enabled = True
        self.width = 8
        self.height = 8

        self.timer = 300

    def update(self) -> None:
        self.sprite.update()

        self.timer -= 1
        if self.timer <= 0:
            self.explode()
        elif self.timer < 60:
            self.sprite.play("Fast")
        elif self.timer < 120:
            self.sprite.play("Medium")

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() + Point(0, -3))

    def explode(self) -> None:
        fx = ExplosionFx.instantiate()
        fx.set_position(self.bbox().center())
        for e in self.scene.entities.active_entities():
            if e.position().distance_to(self.position()) <= 18:
                try:
                    e.damage()
                except:
                    pass
                try:
                    e.cut()
                except:
                    pass
        self.destroy()
