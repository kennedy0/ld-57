from potion import *


from entities.bone import Bone


class BoneSpawner(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("BoneSpawner")
        self.slot = 0

    def spawn(self, delay: int) -> None:
        bone = Bone.instantiate()
        bone.delay = delay

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.white())
