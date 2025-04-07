from potion import *


class StartGameScene(Scene):
    def load_entities(self) -> None:
        from entities.game_manager import GameManager
        from entities.screen_wipe import ScreenWipe
        from entities.start_game_screen import StartGameScreen
        self.entities.add(StartGameScreen())
        self.entities.add(GameManager())
        self.entities.add(ScreenWipe())
