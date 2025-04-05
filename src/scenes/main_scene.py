from potion import *

import game_globals
from entities.game_manager import GameManager
from entities.screen_wipe import ScreenWipe
from entities.camera_controller import CameraController
from entities.mario_brick import MarioBrick
from entities.goomba import Goomba
from entities.player import Player
from entities.mario_coin import MarioCoin


class MainScene(Scene):
    def setup_cameras(self) -> None:
        self.main_camera.get_render_pass("Default").set_clear_color(Color.from_hex("#1c1734"))

    def load_entities(self) -> None:
        self.entities.add(CameraController())
        self.entities.add(Player())
        self.entities.add(GameManager())
        self.entities.add(ScreenWipe())


        # Load this stuff last! EntityList.update() is called here.
        if world := game_globals.LDTK_WORLD_NAME:
            self.name = world
            LDtk.load_simplified(self, f"ldtk/{world}.ldtk")
        else:
            Log.warning("No 'LDTK_WORLD_NAME set'")
            return

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
                    Log.warning(f"Could not swap '{ldtk_entity.name}'")
                    e = None
            if e:
                LDtk.swap_entity(ldtk_entity, e)

    def start(self) -> None:
        for i, level in enumerate(self.levels):
            if i == 0:
                level.set_entities_active(True)
            else:
                level.set_entities_active(False)
