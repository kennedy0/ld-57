from potion import *


class Bridge(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Bridge"
        self.tags.add("Bridge")
        self.sprite = Sprite.from_atlas("atlas.png", "bridge")

        self.segments: list[Point] = []
        self.is_chain_cut = False

        self.timer = 0
        self.max_timer = 10

    def awake(self) -> None:

        for i in range(26):
            x = i * 8
            p = Point(self.x + x, self.y)
            self.segments.append(p)

    def update(self) -> None:
        if self.is_chain_cut:
            self.timer -= 1
            if self.timer <= 0:
                try:
                    self.segments.pop()
                    self.timer = self.max_timer
                except:
                    self.destroy()

    def draw(self, camera: Camera) -> None:
        for p in self.segments:
            self.sprite.draw(camera, p)

    def cut_chain(self) -> None:
        if self.is_chain_cut:
            return

        self.is_chain_cut = True
