from __future__ import annotations

from statistics import median
from typing import Callable, TYPE_CHECKING

import sdl2
from sdl2.sdlgfx import FPSManager

from potion.callback_list import CallbackList
from potion.content import Content
from potion.coroutine import update_coroutines
from potion.data_types.color import Color
from potion.event_manager import EventManager
from potion.game import Game
from potion.gui import gui
from potion.input_manager import InputManager
from potion.keyboard import Keyboard
from potion.log import Log
from potion.renderer import Renderer
from potion.time import Time
from potion.window import Window

if TYPE_CHECKING:
    from potion.scene import Scene


class Engine:
    """ The engine is responsible for running the main event loop. """
    _initialized = False

    # Engine state
    _running = False

    # Time
    _frame = 0
    _framerate = 0

    # FPS
    _fps = 0
    _fps_ticks = 0
    _fps_frames_rendered = 0
    _fps_manager: FPSManager = FPSManager()

    # Debug
    _debug_mode = False

    # Metrics
    _metrics_enabled = True
    _log_metrics = True
    _metrics_updated = False
    _metrics_interval = 3000
    _metrics_timer = 0
    _update_time = 0
    _draw_time = 0
    _update_time_measures = []
    _draw_time_measures = []
    _update_time_summary = (0, 0, 0)
    _draw_time_summary = (0, 0, 0)

    # Scene
    _scene: Scene | None = None
    _next_scene: Scene | None = None

    # Callbacks
    _quit_requested_callbacks = CallbackList("EngineQuitRequested")
    _stop_callbacks = CallbackList("EngineStopRequested")

    @classmethod
    def init(cls, framerate: int) -> None:
        """ Initialize the engine. """
        if cls._initialized:
            raise RuntimeError("The engine has already been initialized.")

        # Initialize SDL subsystems
        import sdl2
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER | sdl2.SDL_INIT_EVENTS)

        # Initialize SDL_image
        import sdl2.sdlimage
        sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG)

        # Initialize SDL_mixer
        import sdl2.sdlmixer
        sdl2.sdlmixer.Mix_OpenAudio(
            sdl2.sdlmixer.MIX_DEFAULT_FREQUENCY,
            sdl2.sdlmixer.MIX_DEFAULT_FORMAT,
            sdl2.sdlmixer.MIX_DEFAULT_CHANNELS,
            2048
        )

        # Limit framerate
        cls._framerate = framerate
        sdl2.sdlgfx.SDL_initFramerate(cls._fps_manager)
        sdl2.sdlgfx.SDL_setFramerate(cls._fps_manager, framerate)

        # Time
        Time.set_engine_framerate(framerate)

        cls._initialized = True

    @classmethod
    def init_default(cls) -> None:
        """ Initialize the engine with default settings. """
        framerate = 60
        cls.init(framerate)
        cls.add_quit_requested_callback(cls.stop)

    @classmethod
    def ensure_init(cls) -> None:
        """ Make sure the engine has been initialized. """
        if not cls._initialized:
            raise RuntimeError("The engine has not been initialized. Make sure to run `Engine.init()`.")

    @classmethod
    def frame(cls) -> int:
        """ The current frame number that the engine is processing. """
        return cls._frame

    @classmethod
    def fps(cls) -> int:
        """ The current framerate that the engine is rendering at. """
        return cls._fps

    @classmethod
    def debug_mode(cls) -> bool:
        """ If debug mode is enabled, . """
        return cls._debug_mode

    @classmethod
    def scene(cls) -> Scene | None:
        """ The current scene that is running in the engine. """
        return cls._scene

    @classmethod
    def load_scene(cls, value: Scene) -> None:
        """ Load a new scene. """
        cls._next_scene = value

    @classmethod
    def reload_scene(cls) -> None:
        """ Reload the current scene.
        This creates a new copy of the current scene, and does not do any graceful cleanup.
        This is untested and probably has horrible side effects, but good for a quick-and-dirty reload.
        """
        if cls._scene:
            new_scene = cls._scene.__class__()
            cls.load_scene(new_scene)

    @classmethod
    def next_scene(cls) -> Scene | None:
        """ The next scene that is about to be loaded. """
        return cls._next_scene

    @classmethod
    def update_time(cls) -> int:
        """ The amount of time (in milliseconds) that it took to run the last update loop.
        This is a debug-only feature; its value will always be 0 in a release build.
        """
        return cls._update_time

    @classmethod
    def draw_time(cls) -> int:
        """ The amount of time (in milliseconds) that it took to run the last draw loop.
        This is a debug-only feature; its value will always be 0 in a release build.
        """
        return cls._draw_time

    @classmethod
    def enable_metrics(cls, value: bool) -> None:
        """ Enable performance metrics calculation.
        This is a debug-only feature; its value will not be used in a release build.
        """
        cls._metrics_enabled = value

    @classmethod
    def log_metrics(cls, value: bool) -> None:
        """ Enable metrics logging.
        This is a debug-only feature; its value will not be used in a release build.
        """
        cls._log_metrics = value

    @classmethod
    def metrics_updated(cls) -> bool:
        """ Returns whether or not the metrics were updated this frame.
        This is a debug-only feature; its value will always be False in a release build.
        """
        return cls._metrics_updated

    @classmethod
    def set_metrics_interval(cls, value: int) -> None:
        """ Set the interval (in milliseconds) that the metrics should be updated.
        This is a debug-only feature; its value will not be used in a release build.
        """
        cls._metrics_interval = value

    @classmethod
    def update_time_summary(cls) -> tuple[int, int, int]:
        """ A summary of the minimum, median, and maximum update times since the last metrics summary was run.
        This is a debug-only feature; its value will always be (0, 0, 0) in a release build.
        """
        return cls._update_time_summary

    @classmethod
    def draw_time_summary(cls) -> tuple[int, int, int]:
        """ A summary of the minimum, median, and maximum draw times since the last metrics summary was run.
        This is a debug-only feature; its value will always be (0, 0, 0) in a release build.
        """
        return cls._draw_time_summary

    @classmethod
    def start(cls, first_scene: Scene) -> None:
        """ Starts the main game loop. """
        # Ensure systems have been initialized
        Game.ensure_init()
        Window.ensure_init()
        Renderer.ensure_init()
        cls.ensure_init()

        # Check for optional GUI initialization
        gui.check_init()

        # Reload content (in case it was loaded before any SDL sub-systems were initialized)
        Content.reload()

        # Set the window title if it hasn't been set
        if not Window.title():
            window_title = f"{Game.name()} {Game.version()}"
            Window.set_title(window_title)

        # Generate the window's viewport texture
        Window.update_viewport()

        # Load the first scene
        cls.load_scene(first_scene)

        # Run the game loop
        cls._running = True
        while cls._running:
            # Globals
            Window.update()
            Time.update()
            InputManager.update()
            EventManager.process_events()

            # Game loop
            cls.update()
            cls.draw()

            # Transition scene
            if cls._scene != cls._next_scene:
                cls._transition_scene()

            # Update frame and fps
            cls._update_frame_counters()
            cls._update_fps()

            # Debug mode
            if __debug__:
                cls._handle_debug_mode_toggle()
                if cls._metrics_enabled:
                    cls._update_metrics()
                    if cls._log_metrics and cls._metrics_updated:
                        cls._write_metrics_log()

            # Limit framerate
            sdl2.sdlgfx.SDL_framerateDelay(cls._fps_manager)

    @classmethod
    def update(cls) -> None:
        """ Update loop. """
        # Start metrics timer
        if __debug__:
            update_time_start = sdl2.timer.SDL_GetTicks64()

        # Update scene
        if cls._scene:
            cls._scene.update()

        # Update coroutines
        update_coroutines()

        # Update metrics
        if __debug__:
            cls._update_time = sdl2.timer.SDL_GetTicks64() - update_time_start  # noqa
            if cls._metrics_enabled:
                cls._update_time_measures.append(cls._update_time)

    @classmethod
    def draw(cls) -> None:
        """ Draw loop. """
        if __debug__:
            draw_time_start = sdl2.timer.SDL_GetTicks64()

        # Clear the screen
        Renderer.unset_render_target()
        Renderer.clear(Color.black())

        # Clear the game viewport
        Renderer.set_render_target(Window.viewport_texture())
        Renderer.clear(Color.black())

        # Draw scene
        if cls._scene:
            cls._scene.draw()

        # Copy the game viewport's texture to the screen
        Renderer.unset_render_target()
        Renderer.copy(
            texture=Window.viewport_texture(),
            source_rect=None,
            destination_rect=Window.viewport(),
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw the GUI to the screen
        gui.draw()
        gui.reset()

        # Update the screen
        Renderer.present()

        if __debug__:
            cls._draw_time = sdl2.timer.SDL_GetTicks64() - draw_time_start  # noqa
            if cls._metrics_enabled:
                cls._draw_time_measures.append(cls._draw_time)

    @classmethod
    def stop(cls) -> None:
        """ Stop the engine if it is running. """
        cls._running = False
        cls.on_stop()

    @classmethod
    def add_quit_requested_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the application sends a quit event. """
        cls._quit_requested_callbacks.append(callback)

    @classmethod
    def remove_quit_requested_callback(cls, callback: Callable) -> None:
        """ Remove a quit requested callback. """
        cls._quit_requested_callbacks.remove(callback)

    @classmethod
    def add_stop_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the engine stops. """
        cls._stop_callbacks.append(callback)

    @classmethod
    def remove_stop_callback(cls, callback: Callable) -> None:
        """ Remove a stop callback. """
        cls._stop_callbacks.remove(callback)

    @classmethod
    def on_quit_requested(cls) -> None:
        """ Called when the application sends a quit event. """
        cls._quit_requested_callbacks.execute_callbacks()

    @classmethod
    def on_stop(cls) -> None:
        """ Called right before the engine stops. """
        cls._stop_callbacks.execute_callbacks()

    @classmethod
    def _transition_scene(cls) -> None:
        """ Called after a scene ends, before the next scene starts. """
        if cls._scene:
            Log.debug(f"Unloading {cls._scene}")
            cls._scene.entities.end()
            cls._scene.end()

        cls._scene = cls._next_scene

        if cls._scene:
            Log.debug(f"Loading {cls._scene}")
            cls._scene.on_load()
            cls._scene.start()

    @classmethod
    def _update_frame_counters(cls) -> None:
        """ Update frame counters. """
        cls._frame += 1
        cls._fps_frames_rendered += 1
        if cls._scene:
            cls._scene._frame += 1  # noqa

    @classmethod
    def _update_fps(cls) -> None:
        """ Calculate and update the frames per second. """
        cls._fps_ticks += Time.delta_time_ms
        if cls._fps_ticks > 1000:
            cls._fps_ticks -= 1000
            cls._fps = cls._fps_frames_rendered
            cls._fps_frames_rendered = 0

    @classmethod
    def _handle_debug_mode_toggle(cls) -> None:
        """ Toggle debug mode on and off. """
        if Keyboard.get_key_down(sdl2.SDLK_BACKQUOTE):
            cls._debug_mode = not cls._debug_mode

    @classmethod
    def _update_metrics(cls) -> None:
        """ Update the performance metrics. """
        cls._metrics_updated = False
        cls._metrics_timer += Time.delta_time_ms
        if cls._metrics_timer >= cls._metrics_interval:
            cls._metrics_updated = True
            cls._metrics_timer = 0
            cls._update_time_summary = (
                min(cls._update_time_measures),
                int(median(cls._update_time_measures)),
                max(cls._update_time_measures)
            )
            cls._draw_time_summary = (
                min(cls._draw_time_measures),
                int(median(cls._draw_time_measures)),
                max(cls._draw_time_measures)
            )
            cls._update_time_measures.clear()
            cls._draw_time_measures.clear()

    @classmethod
    def _write_metrics_log(cls) -> None:
        """ Log the engine's performance metrics. """
        # FPS
        fps = f"{cls._fps:2d} FPS"

        # Frame time graph
        update = '█'
        draw = '▓'
        blank = '░'

        update_time = cls._update_time_summary[1]
        draw_time = cls._draw_time_summary[1]

        bar_graph = ""
        bar_graph += update * update_time
        bar_graph += draw * draw_time

        while len(bar_graph) < 16:
            bar_graph += blank

        # Frame time
        frame_time = f"{update_time + draw_time:2d} ms"

        # Log metrics
        Log.debug(f"{fps} {bar_graph} {frame_time}")
