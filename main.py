import sys

from potion import *

import game_globals
from scenes.main_scene import MainScene
from scenes.start_game_scene import StartGameScene


def main() -> int:
    Game.init(name="LD57", version="v1")
    Engine.init_default()
    Window.init_default()
    Renderer.init_default()
    _init_input()

    # ToDo: CHANGE VALUE HERE FOR TESTING
    game_globals.GO_TO_NEXT_WORLD = True
    # game_globals.NEXT_WORLD_QUEUE.append("mario_world")
    game_globals.NEXT_WORLD_QUEUE.append("zelda_world")
    # game_globals.NEXT_WORLD_QUEUE.append("undertale_world")

    scene = MainScene()
    Engine.start(scene)
    return 0

def _init_input() -> None:
    import sdl2

    Input.add_button("Up")
    Input.map_key_to_button(Keyboard.UP_ARROW, "Up")
    Input.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP, "Up")
    Input.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTY, -1, "Up")

    Input.add_button("Down")
    Input.map_key_to_button(Keyboard.DOWN_ARROW, "Down")
    Input.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN, "Down")
    Input.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTY, 1, "Down")

    Input.add_button("Left")
    Input.map_key_to_button(Keyboard.LEFT_ARROW, "Left")
    Input.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT, "Left")
    Input.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTX, -1, "Left")

    Input.add_button("Right")
    Input.map_key_to_button(Keyboard.RIGHT_ARROW, "Right")
    Input.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT, "Right")
    Input.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTX, 1, "Right")

    Input.add_button("Jump")
    Input.map_key_to_button(Keyboard.SPACE, "Jump")
    Input.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_A, "Jump")

    Input.add_button("Special")
    Input.map_key_to_button(Keyboard.LEFT_SHIFT, "Special")
    Input.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_X, "Special")


if __name__ == "__main__":
    with papp.crash_handler():
        sys.exit(main())
