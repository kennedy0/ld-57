from potion import *

import game_globals
from entities.game_manager import GameManager
from entities.screen_wipe import ScreenWipe
from entities.camera_controller import CameraController
from entities.mario_brick import MarioBrick
from entities.mario_question import MarioQuestion
from entities.moving_platform import MovingPlatform
from entities.invisible_platform import InvisiblePlatform
from entities.goomba import Goomba
from entities.player import Player
from entities.mario_coin import MarioCoin
from entities.grass import Grass
from entities.cracked_block import CrackedBlock
from entities.bomb_shop import BombShop
from entities.shop_fire import ShopFire
from entities.coin_ui import CoinUi
from entities.rupee_ui import RupeeUi
from entities.hearts_ui import HeartsUi


class MainScene(Scene):
    def setup_cameras(self) -> None:
        self.main_camera.get_render_pass("Default").set_clear_color(Color.from_hex("#1c1734"))

    def load_entities(self) -> None:
        self.entities.add(CameraController())
        self.entities.add(Player())
        self.entities.add(GameManager())
        self.entities.add(ScreenWipe())


        # Load this stuff last! EntityList.update() is called here.
        if game_globals.GO_TO_NEXT_WORLD:
            try:
                next_world = game_globals.NEXT_WORLD_QUEUE.pop(0)
            except IndexError:
                Log.warning("game_globals.NEXT_WORLD is empty")
                next_world = ""
        else:

            next_world = game_globals.CURRENT_WORLD

        if next_world:
            self.name = next_world
            game_globals.CURRENT_WORLD = self.name
            game_globals.GO_TO_NEXT_WORLD = False
            LDtk.load_simplified(self, f"ldtk/{next_world}.ldtk")
        else:
            return

        # UI - conditional based on world
        if self.name == "mario_world":
            self.entities.add(CoinUi())
        elif self.name == "zelda_world":
            self.entities.add(RupeeUi())
            self.entities.add(HeartsUi())

        # Load LDTK
        for ldtk_entity in LDtk.ldtk_entities(self):

            custom_fields = ldtk_entity.metadata.get("ldtk_custom_fields")
            if not custom_fields:
                custom_fields = {}

            match ldtk_entity.metadata["ldtk_entity_name"]:
                case "MarioBrick":
                    e = MarioBrick()
                case "MarioQuestion":
                    e = MarioQuestion()
                case "MarioCoin":
                    e = MarioCoin()
                case "Goomba":
                    e = Goomba()
                case "Grass":
                    e = Grass()
                case "BombShop":
                    e = BombShop()
                case "ShopFire":
                    e = ShopFire()
                case "CrackedBlock":
                    e = CrackedBlock()
                case "InvisiblePlatform":
                    e = InvisiblePlatform()
                case "MovingPlatform":
                    e = MovingPlatform()
                    if cycle_time := custom_fields.get("CycleTime"):
                        e.cycle_time = cycle_time
                    if x_distance := custom_fields.get("XDistance"):
                        e.x_distance = x_distance
                    if y_distance := custom_fields.get("YDistance"):
                        e.y_distance = y_distance
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
