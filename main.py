import sys

from potion import *

from scenes.main_scene import MainScene


def main() -> int:
    Game.init(name="LD57", version="v1")
    Engine.init_default()
    Window.init_default()
    Renderer.init_default()

    scene = MainScene()
    Engine.start(scene)
    return 0


if __name__ == "__main__":
    with papp.crash_handler():
        sys.exit(main())
