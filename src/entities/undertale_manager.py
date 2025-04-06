from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player
    from entities.spider_spawner import SpiderSpawner
    from entities.bone_spawner import BoneSpawner
    from entities.undertale_box import UndertaleBox
    from entities.undertale_bg import UndertaleBg


class UndertaleManager(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "UndertaleManager"

        self.player: Player | None = None
        self.undertale_box: UndertaleBox | None = None
        self.undertale_bg: UndertaleBg | None = None
        self.bone_spawners: list[BoneSpawner] = []
        self.spider_spawners: list[SpiderSpawner] = []

        self.walls_created = False

        self.timer = 0

    def start(self) -> None:
        self.player = self.find("Player")
        self.undertale_box = self.find("UndertaleBox")
        self.undertale_bg = self.find("UndertaleBg")
        for entity in self.scene.entities:
            if "BoneSpawner" in entity.tags:
                self.bone_spawners.append(entity)
            if "SpiderSpawner" in entity.tags:
                self.spider_spawners.append(entity)

    def update(self) -> None:
        if not self.walls_created:
            if self.player.grounded:
                self.walls_created = True
                self.undertale_box.create_walls()

        self.timer += 1

        if self.timer == 300:
            pass

        # DEBUG
        if __debug__:
            if Keyboard.get_key_down(Keyboard.SPACE):
                self.undertale_bg.play_transition()

    def spawn_bone(self, slot: int, delay: int) -> None:
        try:
            self.bone_spawners[slot].spawn(delay)
        except Exception as e:
            Log.warning(e)

    def spawn_spider(self, slot: int, delay: int) -> None:
        try:
            self.spider_spawners[slot].spawn(delay)
        except Exception as e:
            Log.warning(e)
