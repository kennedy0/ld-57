from potion import *

from entities.mario_brick import MarioBrick
from entities.goomba import Goomba
from entities.player import Player
from entities.mario_coin import MarioCoin


class MainScene(Scene):
    def setup_cameras(self) -> None:
        self.main_camera.get_render_pass("Default").set_clear_color(Color.from_hex("#1c1734"))

    def load_entities(self) -> None:
        LDtk.load_simplified(self, "ldtk/world.ldtk")

        # Load LDTK
        for ldtk_entity in LDtk.ldtk_entities(self):
            match ldtk_entity.metadata["ldtk_entity_name"]:
                case "MarioBrick":
                    e = MarioBrick()
                case "MarioCoin":
                    e = MarioCoin()
                case "Goomba":
                    e = Goomba()
                case _:
                    e = None
            if e:
                LDtk.swap_entity(ldtk_entity, e)

        self.entities.add(Player())
