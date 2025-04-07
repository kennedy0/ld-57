from potion import *


class EndGameScene(Scene):
    def load_entities(self) -> None:
        from entities.end_game_screen import EndGameScreen
        self.entities.add(EndGameScreen())
