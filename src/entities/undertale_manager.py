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

        self.sfx = SoundEffect("music/undertale.wav")
        self.stopped_music = False

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

        if self.player.hp == 0:
            if not self.stopped_music:
                self.stopped_music = True
                self.sfx.stop()

        self.timer += 1

        if self.timer == 300:
            self.sfx.play()
            self.spawn_bone(0, 0)
        elif self.timer == 438:
            self.spawn_bone(1, 0)
        elif self.timer == 571:
            self.spawn_bone(2, 0)
        elif self.timer == 700:
            self.spawn_bone(3, 0)
        elif self.timer == 835:
            self.spawn_bone(0, 0)
            self.spawn_bone(1, 0)
        elif self.timer == 963:
            self.spawn_bone(2, 0)
            self.spawn_bone(3, 0)
        elif self.timer == 1094:
            self.spawn_bone(0, 0)
            self.spawn_bone(3, 0)
        elif self.timer == 1225:
            self.undertale_bg.play_transition()
            self.spawn_bone(1, 0)
            self.spawn_bone(2, 0)

        elif self.timer == 1353:
            self.spawn_spider(7, 0)
            self.spawn_spider(15, 0)
        elif self.timer == 1425:
            self.spawn_spider(6, 0)
            self.spawn_spider(14, 0)
        elif self.timer == 1488:
            self.spawn_spider(5, 0)
            self.spawn_spider(13, 0)
        elif self.timer == 1554:
            self.spawn_spider(4, 0)
            self.spawn_spider(12, 0)
        elif self.timer == 1617:
            self.spawn_spider(3, 0)
            self.spawn_spider(11, 0)
        elif self.timer == 1682:
            self.spawn_spider(2, 0)
            self.spawn_spider(10, 0)
        elif self.timer == 1747:
            self.spawn_spider(1, 0)
            self.spawn_spider(9, 0)
        elif self.timer == 1813:
            self.spawn_spider(0, 0)
            self.spawn_spider(8, 0)
        elif self.timer == 2100:
            self.undertale_box.destroy_walls()


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
