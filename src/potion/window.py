from ctypes import byref, c_int, POINTER
from enum import Enum
from math import floor
from typing import Callable

import sdl2

from potion.callback_list import CallbackList
from potion.content_types.texture import Texture
from potion.data_types.rect import Rect
from potion.log import Log


class WindowMode(Enum):
    NONE = 0
    WINDOWED = 1
    BORDERLESS_WINDOWED = 2
    FULLSCREEN = 3


class ViewportMode(Enum):
    FREE = 0
    FIT_RENDERER = 1
    MATCH_WINDOW = 2


class Window:
    """ The main window for the application. """
    _initialized = False

    _title = ""

    _sdl_window = None

    _window_mode_change_queued = False
    _next_window_mode = WindowMode.NONE

    # When the window switches from windowed to fullscreen, the last position and size of the window is stored here so
    #   it can be easily restored when switching back.
    _last_windowed_position: tuple[int, int] | None = None
    _last_windowed_size: tuple[int, int] | None = None

    # Viewport
    _viewport: Rect = Rect.empty()
    _viewport_mode: ViewportMode = ViewportMode.FIT_RENDERER
    _viewport_scale: int = 1
    _viewport_texture: Texture | None = None

    # Callbacks
    _resize_callbacks = CallbackList("WindowResize")
    _fullscreen_callbacks = CallbackList("WindowFullscreen")
    _windowed_callbacks = CallbackList("WindowWindowed")
    _viewport_changed_callbacks = CallbackList("WindowViewportChanged")

    @classmethod
    def init(cls, title: str, size: tuple[int, int], flags: int = 0) -> None:
        """ Initialize the window. """
        from potion import Renderer

        if cls._initialized:
            raise RuntimeError("The window has already been initialized.")

        # Create SDL window
        title = title.encode("utf-8")
        x = sdl2.SDL_WINDOWPOS_UNDEFINED
        y = sdl2.SDL_WINDOWPOS_UNDEFINED
        w = int(size[0])
        h = int(size[1])
        cls._sdl_window = sdl2.SDL_CreateWindow(title, x, y, w, h, flags)

        # Initialize the mouse cursors
        from potion.mouse import Mouse
        Mouse.init_cursors()

        # Install callbacks
        cls.add_resize_callback(cls.update_viewport)
        Renderer.add_resolution_change_callback(cls.update_viewport)

        cls._initialized = True

    @classmethod
    def init_default(cls) -> None:
        """ Initialize the window with default settings. """
        size = (1280, 720)
        flags = 0
        flags |= sdl2.SDL_WINDOW_RESIZABLE
        cls.init(title="", size=size, flags=flags)
        cls.add_fullscreen_callback(cls.enable_mouse_grab)
        cls.add_windowed_callback(cls.disable_mouse_grab)

    @classmethod
    def ensure_init(cls) -> None:
        """ Make sure the window has been initialized. """
        if not cls._initialized:
            raise RuntimeError("The window has not been initialized. Make sure to run `Window.init()`.")

    @classmethod
    def title(cls) -> str:
        """ The window title. """
        title = sdl2.SDL_GetWindowTitle(cls._sdl_window)
        return title.decode("utf-8")

    @classmethod
    def set_title(cls, title: str) -> None:
        """ Set the window title. """
        sdl2.SDL_SetWindowTitle(cls._sdl_window, title.encode("utf-8"))

    @classmethod
    def position(cls) -> tuple[int, int]:
        """ The position of the window. """
        x = c_int()
        y = c_int()
        sdl2.SDL_GetWindowPosition(cls._sdl_window, byref(x), byref(y))
        return int(x.value), int(y.value)

    @classmethod
    def set_position(cls, position: tuple[int, int]) -> None:
        x = int(position[0])
        y = int(position[1])
        sdl2.SDL_SetWindowPosition(cls._sdl_window, x, y)

    @classmethod
    def size(cls) -> tuple[int, int]:
        """ The window size. """
        w = c_int()
        h = c_int()
        sdl2.SDL_GetWindowSize(cls._sdl_window, byref(w), byref(h))
        return int(w.value), int(h.value)

    @classmethod
    def set_size(cls, size: tuple[int, int]) -> None:
        """ Set the window size. """
        w = int(size[0])
        h = int(size[1])
        sdl2.SDL_SetWindowSize(cls._sdl_window, w, h)

    @classmethod
    def width(cls) -> int:
        """ The window width. """
        return cls.size()[0]

    @classmethod
    def height(cls) -> int:
        """ The window height. """
        return cls.size()[1]

    @classmethod
    def is_windowed(cls) -> bool:
        """ Returns True if the window is in windowed mode. """
        flags = sdl2.SDL_GetWindowFlags(cls._sdl_window)
        return not flags & sdl2.SDL_WINDOW_FULLSCREEN

    @classmethod
    def is_borderless_windowed(cls) -> bool:
        """ Returns True if the window is in fullscreen desktop mode. """
        flags = sdl2.SDL_GetWindowFlags(cls._sdl_window)
        return flags & sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP == sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP

    @classmethod
    def is_fullscreen(cls) -> bool:
        """ Returns True if the window is in fullscreen mode. """
        flags = sdl2.SDL_GetWindowFlags(cls._sdl_window)
        return flags & sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP == sdl2.SDL_WINDOW_FULLSCREEN

    @classmethod
    def sdl_window(cls) -> POINTER(sdl2.SDL_Window):
        """ Pointer to the SDL window object. """
        return cls._sdl_window

    @classmethod
    def viewport(cls) -> Rect:
        """ The region of the window that the game draws to.
        The size of the viewport will always be *at least* the game resolution, but may be scaled higher in fixed
            increments (1x, 2x, 3x, etc.) to best fit inside the window.
        """
        return cls._viewport

    @classmethod
    def set_viewport(cls, viewport: Rect) -> None:
        """ Set the viewport rect.
        This can only be done when the viewport mode is FREE.
        """
        if not cls._viewport_mode == ViewportMode.FREE:
            Log.error("Viewport mode must be FREE to use set_viewport()")

        cls._viewport = viewport
        cls.update_viewport()

    @classmethod
    def viewport_mode(cls) -> ViewportMode:
        """ The mode that the viewport uses to calculate its size. """
        return cls._viewport_mode

    @classmethod
    def set_viewport_mode_free(cls) -> None:
        """ Set the viewport mode to FREE.
        The viewport must be set manually with `set_viewport()`.
        """
        cls._viewport_mode = ViewportMode.FREE
        cls.update_viewport()

    @classmethod
    def set_viewport_mode_fit_renderer(cls) -> None:
        """ Set the viewport mode to FIT_RENDERER.
        The viewport will always be a pixel-perfect increment of the Renderer's resolution.
        """
        cls._viewport_mode = ViewportMode.FIT_RENDERER
        cls.update_viewport()

    @classmethod
    def set_viewport_mode_match_window(cls) -> None:
        """ Set the viewport mode to MATCH_WINDOW.
        The viewport size will always match the window size.
        """
        cls._viewport_mode = ViewportMode.MATCH_WINDOW
        cls.update_viewport()

    @classmethod
    def viewport_scale(cls) -> int:
        """ The scale of the viewport, relative to the game resolution.
        This is only calculated / used if the viewport mode is FIT_RENDERER
        """
        return cls._viewport_scale

    @classmethod
    def viewport_texture(cls) -> Texture:
        """ The texture that all cameras in the game render to. """
        return cls._viewport_texture

    @classmethod
    def show(cls) -> None:
        """ Show the window. """
        sdl2.SDL_ShowWindow(cls._sdl_window)

    @classmethod
    def focus(cls) -> None:
        """ Raise the window above other windows and set the input focus. """
        sdl2.SDL_RaiseWindow(cls._sdl_window)

    @classmethod
    def hide(cls) -> None:
        """ Hide the window. """
        sdl2.SDL_HideWindow(cls._sdl_window)

    @classmethod
    def close(cls) -> None:
        """ Close the window. """
        sdl2.SDL_DestroyWindow(cls._sdl_window)

    @classmethod
    def set_windowed(cls) -> None:
        """ Set the window mode to windowed. """
        cls._window_mode_change_queued = True
        cls._next_window_mode = WindowMode.WINDOWED

    @classmethod
    def set_borderless_windowed(cls) -> None:
        """ Set the window mode to borderless windowed.
        This is a 'fake' fullscreen that takes the size of the desktop.
        """
        cls._window_mode_change_queued = True
        cls._next_window_mode = WindowMode.BORDERLESS_WINDOWED

    @classmethod
    def set_fullscreen(cls) -> None:
        """ Set the window mode to fullscreen.
        This is a 'real' fullscreen with a video mode change.
        """
        cls._window_mode_change_queued = True
        cls._next_window_mode = WindowMode.FULLSCREEN

    @classmethod
    def enable_mouse_grab(cls) -> None:
        """ Confine the mouse to the window. """
        sdl2.SDL_SetWindowGrab(cls._sdl_window, sdl2.SDL_TRUE)

    @classmethod
    def disable_mouse_grab(cls) -> None:
        """ Disable the mouse grab setting. """
        sdl2.SDL_SetWindowGrab(cls._sdl_window, sdl2.SDL_FALSE)

    @classmethod
    def update(cls) -> None:
        """ Run deferred window mode updates.
        This should be called at the beginning of the game loop.
        """
        # Window mode change
        if cls._window_mode_change_queued:
            match cls._next_window_mode:
                case WindowMode.WINDOWED:
                    cls._set_windowed()
                case WindowMode.BORDERLESS_WINDOWED:
                    cls._set_borderless_windowed()
                case WindowMode.FULLSCREEN:
                    cls._set_fullscreen()
                case _:
                    pass
            cls._window_mode_change_queued = False
            cls._next_window_mode = WindowMode.NONE

    @classmethod
    def update_viewport(cls) -> None:
        """ Calculate and update the viewport.
        This needs to be called:
            - Once before the game loop starts in order to initialize the viewport and texture
            - Any time the render targets reset or render device reset event occurs
            - Any time the viewport mode changes
        """
        match cls._viewport_mode:
            case ViewportMode.FREE:
                cls._update_viewport_free()
            case ViewportMode.FIT_RENDERER:
                cls._update_viewport_fit_renderer()
            case ViewportMode.MATCH_WINDOW:
                cls._update_viewport_match_window()

        cls.on_viewport_changed()

    @classmethod
    def _update_viewport_free(cls) -> None:
        cls._viewport_scale = 1
        cls._viewport_texture = Texture.create_target(cls.viewport().width, cls.viewport().height)

    @classmethod
    def _update_viewport_fit_renderer(cls) -> None:
        from potion.renderer import Renderer

        window_w = cls.width()
        window_h = cls.height()

        center_x = floor(window_w / 2)
        center_y = floor(window_h / 2)

        resolution_x, resolution_y = Renderer.resolution()

        # Calculate scale
        scale_x = window_w / resolution_x
        scale_y = window_h / resolution_y
        scale = min(scale_x, scale_y)

        # Floor the result for pixel-perfect scaling (increments of 1x, 2x, 3x, etc.)
        scale = floor(scale)
        if scale < 1:
            scale = 1

        # Viewport dimensions
        w = resolution_x * scale
        h = resolution_y * scale
        x = center_x - floor(w / 2)
        y = center_y - floor(h / 2)

        # Update viewport
        cls._viewport = Rect(x, y, w, h)
        cls._viewport_scale = scale
        cls._viewport_texture = Texture.create_target(int(w), int(h))

    @classmethod
    def _update_viewport_match_window(cls) -> None:
        cls._viewport = Rect(0, 0, cls.width(), cls.height())
        cls._viewport_scale = 1
        cls._viewport_texture = Texture.create_target(cls.width(), cls.height())

    @classmethod
    def add_resize_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the window changes size. """
        cls._resize_callbacks.append(callback)

    @classmethod
    def remove_resize_callback(cls, callback: Callable) -> None:
        """ Remove a resize callback. """
        cls._resize_callbacks.remove(callback)

    @classmethod
    def add_viewport_changed_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the viewport changes. """
        cls._viewport_changed_callbacks.append(callback)

    @classmethod
    def remove_viewport_changed_callback(cls, callback: Callable) -> None:
        """ Remove a viewport changed callback. """
        cls._viewport_changed_callbacks.remove(callback)

    @classmethod
    def add_fullscreen_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the window is set to fullscreen mode. """
        cls._fullscreen_callbacks.append(callback)

    @classmethod
    def remove_fullscreen_callback(cls, callback: Callable) -> None:
        """ Remove a fullscreen callback. """
        cls._fullscreen_callbacks.remove(callback)

    @classmethod
    def add_windowed_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the window is set to windowed mode. """
        cls._windowed_callbacks.append(callback)

    @classmethod
    def remove_windowed_callback(cls, callback: Callable) -> None:
        """ Remove a windowed callback. """
        cls._windowed_callbacks.remove(callback)

    @classmethod
    def on_window_resized(cls) -> None:
        """ Called when the window changes size. """
        cls._resize_callbacks.execute_callbacks()

    @classmethod
    def on_window_fullscreen(cls) -> None:
        """ Called when the window is set to fullscreen mode. """
        cls._fullscreen_callbacks.execute_callbacks()

    @classmethod
    def on_window_windowed(cls) -> None:
        """ Called when the window is set to windowed mode. """
        cls._windowed_callbacks.execute_callbacks()

    @classmethod
    def on_viewport_changed(cls) -> None:
        """ Called when the viewport changes. """
        cls._viewport_changed_callbacks.execute_callbacks()

    @classmethod
    def _set_windowed(cls) -> None:
        """ Execute the queued change to windowed mode. """
        # Restore the window position and size
        if cls._last_windowed_position:
            cls.set_position(cls._last_windowed_position)
        if cls._last_windowed_size:
            cls.set_size(cls._last_windowed_size)

        # Set the window to windowed
        sdl2.SDL_SetWindowFullscreen(cls._sdl_window, 0)

        # Invoke callbacks
        cls.on_window_resized()
        cls.on_window_windowed()

    @classmethod
    def _set_borderless_windowed(cls) -> None:
        """ Execute the queued change to borderless windowed mode. """
        # Store the window size and position if we're in windowed mode
        if cls.is_windowed():
            cls._last_windowed_position = cls.position()
            cls._last_windowed_size = cls.size()

        # Set the window to fullscreen desktop
        sdl2.SDL_SetWindowFullscreen(cls._sdl_window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)

        # Invoke callbacks
        cls.on_window_resized()
        cls.on_window_fullscreen()

    @classmethod
    def _set_fullscreen(cls) -> None:
        """ Execute the queued change to fullscreen mode. """
        # Store the window size and position if we're in windowed mode
        if cls.is_windowed():
            cls._last_windowed_position = cls.position()
            cls._last_windowed_size = cls.size()

        # Get display mode information from current monitor
        display_index = sdl2.SDL_GetWindowDisplayIndex(cls._sdl_window)
        display_bounds = sdl2.SDL_Rect()
        sdl2.SDL_GetDisplayBounds(display_index, display_bounds)

        # Set window size to match display
        sdl2.SDL_SetWindowSize(cls._sdl_window, display_bounds.w, display_bounds.h)
        sdl2.SDL_SetWindowPosition(cls._sdl_window, display_bounds.x, display_bounds.y)

        # Set fullscreen display mode
        display_mode = sdl2.SDL_DisplayMode()
        sdl2.SDL_GetDesktopDisplayMode(display_index, display_mode)
        sdl2.SDL_SetWindowDisplayMode(cls._sdl_window, display_mode)

        # Set window to fullscreen
        sdl2.SDL_SetWindowFullscreen(cls._sdl_window, sdl2.SDL_WINDOW_FULLSCREEN)

        # Invoke callbacks
        cls.on_window_resized()
        cls.on_window_fullscreen()
