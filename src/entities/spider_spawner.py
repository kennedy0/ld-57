from potion import *


from entities.spider import Spider


class SpiderSpawner(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("SpiderSpawner")
        self.slot = 0

    def spawn(self, delay: int) -> None:
        spider = Spider.instantiate()
        spider.delay = delay
        if self.slot > 7:
            spider.x_direction = -1

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.white())
