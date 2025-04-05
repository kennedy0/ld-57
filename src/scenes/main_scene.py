from potion import *

from entities.player import Player


class MainScene(Scene):
    def setup_cameras(self) -> None:
        self.main_camera.get_render_pass("Default").set_clear_color(Color.from_hex("#1c1734"))

    def load_entities(self) -> None:
        LDtk.load_simplified(self, "ldtk/world.ldtk")

        # Load LDTK
        for ldtk_entity in LDtk.ldtk_entities(self):
            pass
            # if ldtk_entity.metadata['ldtk_entity_name'] == "Door":
            #     door = Door()
            #     LDtk.swap_entity(ldtk_entity, door)

        self.entities.add(Player())
