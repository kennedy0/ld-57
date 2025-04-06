from potion import *


class Axe(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Axe")
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "axe")
        self.sprite.play("default")
        self.sprite_offset = Point(-8, 0)

        self.collisions_enabled = True
        self.width = 16
        self.height = 16

    def update(self) -> None:
        self.sprite.update()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() + self.sprite_offset)

    def on_collision_begin(self, other: Entity) -> None:
        if other.name == "Player":
            for e in self.scene.entities:
                if "Bridge" in e.tags:
                    try:
                        other.game_over = True
                        e.cut_chain()
                        self.destroy()
                        boss = self.find("Boss")
                        boss.game_over = True
                    except Exception as e:
                        Log.error(e)
