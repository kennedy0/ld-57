from potion import *

import game_globals


class StartGameScreen(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = Sprite.from_atlas("atlas.png", "start_screen")

    def update(self) -> None:
        if Input.get_button_down("Jump"):
            game_globals.GO_TO_NEXT_WORLD = True
            game_globals.NEXT_WORLD_QUEUE.append("mario_world")
            from scenes.main_scene import MainScene
            Engine.load_scene(MainScene())

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
