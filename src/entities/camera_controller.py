from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class CameraController(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.player: Player | None = None
        self.screen = 0

        self.screen_width = 320
        self.screen_height = 180

        self.pausable = False
        self.is_scrolling = False
        self.scroll_timer = 0
        self.scroll_timer_max = 40

        self.from_level = 0
        self.to_level = 0

        self.from_x = 0
        self.to_x = 0

        self.mario_sfx = SoundEffect("music/mario.wav")
        self.zelda_sfx = SoundEffect("music/zelda.wav")
        self.dark_souls_sfx = SoundEffect("music/darksouls.wav")
        self.sfx_timer = 0
        self.sfx_timer_max = 180

        self._dark_souls_fix = False

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        self.sfx_timer -= 1
        if self.sfx_timer <= 0:
            self.sfx_timer = 0

        if self.is_scrolling:
            self.scroll_timer -= 1
            if self.scroll_timer <= 0:
                self.scene.main_camera.x = self.to_x
                self.is_scrolling = False
                self.scene.paused = False
                self.deactivate_level(self.from_level)
            else:
                t = (self.scroll_timer_max - self.scroll_timer) / self.scroll_timer_max
                self.scene.main_camera.x = pmath.smooth_step(self.from_x, self.to_x, t)
        else:
            screen = self.player.x // self.screen_width
            if screen != self.screen:
                self.scroll(self.screen, screen)

    def scroll(self, from_screen: int, to_screen: int) -> None:
        if self.is_scrolling:
            return

        self.scene.paused = True
        self.scroll_timer = self.scroll_timer_max
        self.is_scrolling = True
        self.screen = to_screen
        self.from_level = from_screen
        self.to_level = to_screen
        self.from_x = from_screen * self.screen_width
        self.to_x = to_screen * self.screen_width
        self.activate_level(to_screen)

        if self.sfx_timer <= 0:
            if self.scene.name == "mario_world":
                self.mario_sfx.play()
                self.sfx_timer = self.sfx_timer_max
            elif self.scene.name == "zelda_world":
                self.zelda_sfx.play()
                self.sfx_timer = self.sfx_timer_max
            elif self.scene.name == "dark_souls_world":
                self.dark_souls_sfx.play()
                self.sfx_timer = self.sfx_timer_max
                if not self._dark_souls_fix:
                    self._dark_souls_fix = True
                    if self.player.y > 129:
                        self.player.y = 129

    def activate_level(self, level: int) -> None:
        for i, l in enumerate(self.scene.levels):
            if i == level:
                l.set_entities_active(True)

    def deactivate_level(self, level: int) -> None:
        for i, l in enumerate(self.scene.levels):
            if i == level:
                l.set_entities_active(False)
