from __future__ import annotations

from potion import *

import game_globals

if TYPE_CHECKING:
    from entities.screen_wipe import ScreenWipe



class GameManager(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "GameManager"
        self.pausable = False

        self.is_loading = False
        self.is_reloading = False
        self.is_transitioning_to_next_world = False
        self.screen_wipe: ScreenWipe | None = None

        self.transition_buffer_timer = 0
        self.transition_buffer_timer_max = 60

    def start(self) -> None:
        self.screen_wipe = self.find("ScreenWipe")
        self.load_scene()

    def load_scene(self) -> None:
        self.is_loading = True
        self.scene.paused = True
        self.screen_wipe.show()

    def reload_scene(self) -> None:
        self.is_reloading = True
        self.scene.paused = True
        self.screen_wipe.hide()

    def load_next_world(self) -> None:
        self.is_transitioning_to_next_world = True
        self.scene.paused = True
        self.screen_wipe.hide()

    def update(self) -> None:
        if self.is_loading or self.is_reloading or self.is_transitioning_to_next_world:
            if not self.screen_wipe.is_transitioning:
                self.is_loading = False
                self.scene.paused = False
                if self.is_reloading:
                    Engine.reload_scene()
                if self.is_transitioning_to_next_world:
                    if not game_globals.NEXT_SCENE_IS_TRANSITION_SCENE:
                        self.set_next_world_name()
                    Engine.reload_scene()

    def set_next_world_name(self) -> None:
        if self.scene.name == "mario_world":
            game_globals.LDTK_WORLD_NAME = "zelda_world"
