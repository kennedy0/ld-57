from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.screen_wipe import ScreenWipe



class GameManager(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "GameManager"
        self.pausable = False

        self.is_loading = False
        self.is_reloading = False
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

    def update(self) -> None:
        if self.is_loading or self.is_reloading:
            if not self.screen_wipe.is_transitioning:
                self.is_loading = False
                self.scene.paused = False
                if self.is_reloading:
                    Engine.reload_scene()
