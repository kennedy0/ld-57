from potion import *


class BombShop(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = Sprite.from_atlas("atlas.png", "bomb_shop")
        self.sold_out_sprite = Sprite.from_atlas("atlas.png", "bomb_shop_sold_out")

        self.sold_out = False

        self.collisions_enabled = True
        self.width = 24
        self.height = 24

    def update(self) -> None:
        if self.sold_out:
            if player := self.find("Player"):
                try:
                    if not player.has_bomb:
                        self.sold_out = False
                except:
                    pass

    def draw(self, camera: Camera) -> None:
        if self.sold_out:
            self.sold_out_sprite.draw(camera, self.position())
        else:
            self.sprite.draw(camera, self.position())

    def on_collision_begin(self, other: Entity) -> None:
        if other.name == "Player":
            try:
                if other.rupees >= 50:
                    other.rupees -= 50
                    other.has_bomb = True
                    self.sold_out = True
            except:
                pass
