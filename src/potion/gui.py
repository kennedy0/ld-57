from __future__ import annotations

import math
import re
from collections import deque
from contextlib import contextmanager
from typing import Any, Generator, TypedDict, TYPE_CHECKING

from potion.bitmap_font import BitmapFont
from potion.clipboard import Clipboard
from potion.content_types.texture import Texture
from potion.data_types.blend_mode import BlendMode
from potion.data_types.circle import Circle
from potion.data_types.color import Color
from potion.data_types.line import Line
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.data_types.scale_mode import ScaleMode
from potion.input_manager import InputManager
from potion.keyboard import Keyboard
from potion.log import Log
from potion.mouse import Mouse
from potion.renderer import Renderer
from potion.sprite import Sprite
from potion.text import Text
from potion.time import Time
from potion.utilities import pmath
from potion.window import Window

if TYPE_CHECKING:
    from potion.camera import Camera


# Layout
LAYOUT_NONE       = 0  # noqa
LAYOUT_VERTICAL   = 1  # noqa
LAYOUT_HORIZONTAL = 2  # noqa
LAYOUT_GRID       = 3  # noqa

# Layers
LAYER_NONE   = 0  # noqa
LAYER_WINDOW = 1  # noqa
LAYER_MENU   = 2  # noqa
LAYER_MODAL  = 3  # noqa

# Input
INPUT_CURSOR_BLINK_SPEED = 530

# Mouse cursor
MOUSE_CURSOR_ARROW                = 0   # noqa
MOUSE_CURSOR_TEXT_SELECT          = 1   # noqa
MOUSE_CURSOR_WAIT                 = 2   # noqa
MOUSE_CURSOR_WAIT_ARROW           = 3   # noqa
MOUSE_CURSOR_CROSSHAIR            = 4   # noqa
MOUSE_CURSOR_RESIZE_DIAGONAL_DOWN = 5   # noqa
MOUSE_CURSOR_RESIZE_DIAGONAL_UP   = 6   # noqa
MOUSE_CURSOR_RESIZE_HORIZONTAL    = 7   # noqa
MOUSE_CURSOR_RESIZE_VERTICAL      = 8   # noqa
MOUSE_CURSOR_RESIZE_ALL           = 9   # noqa
MOUSE_CURSOR_NO                   = 10  # noqa
MOUSE_CURSOR_HAND                 = 11  # noqa

MOUSE_CURSOR_DISPATCH = {
    MOUSE_CURSOR_ARROW: Mouse.set_cursor_arrow,
    MOUSE_CURSOR_TEXT_SELECT: Mouse.set_cursor_text_select,
    MOUSE_CURSOR_WAIT: Mouse.set_cursor_wait,
    MOUSE_CURSOR_WAIT_ARROW: Mouse.set_cursor_wait_arrow,
    MOUSE_CURSOR_CROSSHAIR: Mouse.set_cursor_crosshair,
    MOUSE_CURSOR_RESIZE_DIAGONAL_DOWN: Mouse.set_cursor_resize_diagonal_down,
    MOUSE_CURSOR_RESIZE_DIAGONAL_UP: Mouse.set_cursor_resize_diagonal_up,
    MOUSE_CURSOR_RESIZE_HORIZONTAL: Mouse.set_cursor_resize_horizontal,
    MOUSE_CURSOR_RESIZE_VERTICAL: Mouse.set_cursor_resize_vertical,
    MOUSE_CURSOR_RESIZE_ALL: Mouse.set_cursor_resize_all,
    MOUSE_CURSOR_NO: Mouse.set_cursor_no,
    MOUSE_CURSOR_HAND: Mouse.set_cursor_hand,
}

# Split Direction
SPLIT_LEFT   = 0  # noqa
SPLIT_RIGHT  = 1  # noqa
SPLIT_TOP    = 2  # noqa
SPLIT_BOTTOM = 3  # noqa

# Mouse Scroll
MOUSE_SCROLL_SPEED = 8

# Sizes
# The sizes in the GUI system are hard-coded, and assume a 16 point pixel font
LABEL_WIDTH = 100

BUTTON_X_PADDING = 8
BUTTON_Y_PADDING = 2
BUTTON_RADIUS = 3
BUTTON_DEPTH = 2

COLOR_BUTTON_WIDTH = 12
COLOR_BUTTON_HEIGHT = 12
COLOR_BUTTON_RADIUS = 2

BUTTON_GROUP_SPACING = 1

TAB_X_PADDING = 2
TAB_Y_PADDING = 1
TAB_RADIUS = 3
TAB_SPACING = 2

CHECKBOX_SIZE = 12
CHECKBOX_RADIUS = 2
CHECKBOX_CHECKMARK_WIDTH = 2
CHECKBOX_CHECKMARK_P0 = Point(2, 6)
CHECKBOX_CHECKMARK_P1 = Point(5, 9)
CHECKBOX_CHECKMARK_P2 = Point(11, 3)

TOGGLE_SWITCH_HEIGHT = 12
TOGGLE_SWITCH_WIDTH = 24
TOGGLE_SWITCH_RADIUS = 5
TOGGLE_SWITCH_HANDLE_SIZE = 10
TOGGLE_SWITCH_HANDLE_RADIUS = 5

SLIDER_HANDLE_WIDTH = 6
SLIDER_HANDLE_HEIGHT = 12
SLIDER_HANDLE_RADIUS = 2
SLIDER_TRACK_HEIGHT = 4

COLOR_BOX_PICKER_RADIUS = 2

COMBO_BOX_RADIUS = 8
COMBO_BOX_ARROW_WIDTH = 8
COMBO_BOX_ARROW_HEIGHT = 4
COMBO_BOX_MENU_HEIGHT = 100

LIST_BOX_CONTENT_PADDING = 2
LIST_BOX_ITEM_X_PADDING = 4
LIST_BOX_ITEM_Y_PADDING = 2
LIST_BOX_ITEM_BACKGROUND_RADIUS = 3

INPUT_RADIUS = 3
INPUT_CONTENT_PADDING = 2
INPUT_LABEL_X_PADDING = 8

GROUP_BOX_CONTENT_PADDING = 2

SPLITTER_THICKNESS = 3
SPLITTER_LENGTH = 16

BOX_RADIUS = 3

SCROLL_AREA_CONTENT_PADDING = 1
SCROLL_BAR_THICKNESS = 6
SCROLL_BAR_MINIMUM_LENGTH = 8
SCROLL_BAR_RADIUS = 2

WINDOW_RADIUS = 3
WINDOW_TITLE_BAR_HEIGHT = 16
WINDOW_CONTENT_PADDING = 2
WINDOW_CLOSE_BUTTON_X_P0 = Point(5, 4)
WINDOW_CLOSE_BUTTON_X_P1 = Point(11, 10)
WINDOW_CLOSE_BUTTON_X_P2 = Point(5, 10)
WINDOW_CLOSE_BUTTON_X_P3 = Point(11, 4)
WINDOW_RESIZE_HANDLE_SIZE = 10
WINDOW_RESIZE_HANDLE_P0 = Point(-9, 0)
WINDOW_RESIZE_HANDLE_P1 = Point(-1, 0)
WINDOW_RESIZE_HANDLE_P2 = Point(0, -1)
WINDOW_RESIZE_HANDLE_P3 = Point(0, -9)

MENU_RADIUS = 3
MENU_CONTENT_PADDING = 4

MENU_ITEM_RADIUS = 3
MENU_ITEM_X_PADDING = 4
MENU_ITEM_Y_PADDING = 2

SUB_MENU_ARROW_SPACING = 16
SUB_MENU_ARROW_WIDTH = 4
SUB_MENU_ARROW_HEIGHT = 8


class GuiCamera:
    """ A specialized camera that allows drawable objects (Text, Sprite, etc.) to be rendered in the GUI. """

    # noinspection PyMethodMayBeStatic
    def world_to_render_position(self, position: Point) -> Point:
        return position


class GuiColors:
    """ A class containing GUI color presets. """
    white = Color.from_hex("#f0f0f0")
    black = Color.from_hex("#16191f")

    gray_light = Color.from_hex("#d7dce4")
    gray = Color.from_hex("#abb2bf")
    gray_dark = Color.from_hex("#9197a3")
    gray_darker = Color.from_hex("#636a77")
    gray_darkest = Color.from_hex("#282c34")

    red_light = Color.from_hex("#f79aa1")
    red = Color.from_hex("#e06c75")
    red_dark = Color.from_hex("#b44e48")
    red_darker = Color.from_hex("#763b3b")
    red_darkest = Color.from_hex("#501e1e")

    green_light = Color.from_hex("#c5e5ad")
    green = Color.from_hex("#98c379")
    green_dark = Color.from_hex("#599b5e")
    green_darker = Color.from_hex("#48674a")
    green_darkest = Color.from_hex("#48674a")

    blue_light = Color.from_hex("#8fd3ff")
    blue = Color.from_hex("#61afef")
    blue_dark = Color.from_hex("#4d65b4")
    blue_darker = Color.from_hex("#484a77")
    blue_darkest = Color.from_hex("#323353")

    cyan_light = Color.from_hex("#9fd2d8")
    cyan = Color.from_hex("#56b6c2")
    cyan_dark = Color.from_hex("#3f858e")
    cyan_darker = Color.from_hex("#3a5762")
    cyan_darkest = Color.from_hex("#212f34")

    purple_light = Color.from_hex("#e8bef5")
    purple = Color.from_hex("#c678dd")
    purple_dark = Color.from_hex("#9d57a7")
    purple_darker = Color.from_hex("#624167")
    purple_darkest = Color.from_hex("#402d43")

    yellow_light = Color.from_hex("#f7dba5")
    yellow = Color.from_hex("#e5c07b")
    yellow_dark = Color.from_hex("#b9995d")
    yellow_darker = Color.from_hex("#817052")
    yellow_darkest = Color.from_hex("#584c36")


class Widget(TypedDict):
    name: str           # The widget name, used as a unique identifier
    rect: Rect          # The widget geometry
    hovered: bool       # True if the mouse is hovering over the widget
    pressed: bool       # True on the frame the mouse presses down on the widget
    held: bool          # True if the widget was pressed and the mouse hasn't been released
    dragged: bool       # True if the mouse moved while the widget is held
    drag_start: Point   # The position of the widget when it entered the dragged state
    released: bool      # True on the frame the mouse releases from the widget
    clicked: bool       # True if the mouse was pressed and released while hovering


# noinspection PyPep8Naming
class gui:
    _initialized = False
    _font = ""
    _line_height = 0
    _zoom = 1
    _camera = None
    _texture = None
    _window_texture = None
    _menu_texture = None
    _modal_texture = None
    _null_texture = None
    _width = 0
    _height = 0
    _region = Rect.empty()
    _disabled = False
    _modal: str | None = None

    # Stacks
    _cursor_stack: deque[Point] = deque()
    _layout_stack: deque[int] = deque()
    _scroll_area_stack: deque[str] = deque()
    _bbox_stack: deque[list[int] | None] = deque()  # [x_min, x_max, y_min, y_max]
    _window_stack: deque[str] = deque()
    _menu_stack: deque[str] = deque()
    _layer_stack: deque[int] = deque()
    _sub_region_stack: dict[int, deque[Rect]] = {
        LAYER_NONE: deque(),
        LAYER_WINDOW: deque(),
        LAYER_MENU: deque(),
        LAYER_MODAL: deque(),
    }

    # Cursor
    _cx = 0
    _cy = 0

    # Layout
    _spacing_x = 8
    _spacing_y = 4
    _grid_columns = 0
    _grid_x = 0
    _grid_y = 0
    _grid_column_width = 0
    _grid_row_height = 0
    _grid_index = 0

    # Bounding box
    _bbox: Rect | None = None
    _calculating_bbox = False

    # Mouse state
    _previous_mouse_position = Point.zero()  # The mouse position from the previous frame
    _left_mouse_pressed = False       # True if the left mouse button was pressed this frame
    _left_mouse_released = False      # True if the left mouse button was released this frame
    _mouse_delta = Point.zero()       # The amount the mouse has moved this frame
    _mouse_drag_start = Point.zero()  # The position of the mouse when it started dragging a widget
    _mouse_drag_delta = Point.zero()  # The difference between the mouse's current position and the drag start position
    _mouse_scroll_wheel = 0           # The amount the scroll wheel has moved this frame
    _mouse_is_over_menu = False       # True if the mouse is currently over a menu

    # Mouse cursor
    _mouse_cursor = MOUSE_CURSOR_ARROW
    _previous_mouse_cursor = MOUSE_CURSOR_ARROW

    # GUI items that were created this frame
    _names: set[str] = set()

    # Caches
    _widget_cache: dict[str, Widget] = {}
    _text_cache: dict[str, Text] = {}
    _data_cache: dict[str, dict] = {}

    # Global states
    _current_widget: str | None = None      # The name of the widget that was just created
    _hovering: str | None = None            # The name of the widget being hovered
    _hovered_last_frame: str | None = None  # The name of the widget that was hovered last frame
    _hovered_layer: int = 0                 # The GUI layer that is being hovered
    _open_windows: set[str] = set()         # The windows that are currently open
    _open_menus: set[str] = set()           # The menus that are currently open
    _menu_depth: int = 0                    # The current menu depth; for sub-menu management
    _textures_reset: bool = False           # True if the textures were reset this frame

    # Debug
    _uninitialized_warning_shown = False

    # Style
    color = GuiColors()
    _style: dict[str, Color] = {
        # General
        'line': color.gray_dark,
        'background': color.gray_darkest,
        'outline': color.gray,

        # Text
        'text': color.gray,
        'text_disabled': color.gray_darker,

        # Label
        'label': color.yellow,

        # URL
        'url': color.purple,
        'url_hovered': color.purple_light,
        'url_pressed': color.purple_dark,
        'url_disabled': color.gray_darker,

        # Button
        'button': color.blue,
        'button_hovered': color.blue_light,
        'button_pressed': color.blue_dark,
        'button_shadow': color.black,
        'button_text': color.gray_darkest,
        'button_disabled': color.gray_darker,

        # Color Button
        'color_button': color.gray,
        'color_button_hovered': color.gray_light,
        'color_button_pressed': color.gray_dark,
        'color_button_shadow': color.black,
        'color_button_disabled': color.gray_darker,

        # Checkbox
        'checkbox_off': color.black,
        'checkbox_on': color.blue_dark,
        'checkbox_hovered': color.blue,
        'checkbox_checkmark': color.gray,
        'checkbox_on_disabled': color.gray_darker,

        # Toggle
        'toggle_handle': color.blue,
        'toggle_handle_hovered': color.blue_light,
        'toggle_handle_pressed': color.blue,
        'toggle_track': color.black,
        'toggle_track_fill': color.blue_dark,
        'toggle_handle_disabled': color.gray,
        'toggle_track_fill_disabled': color.gray_darker,

        # Slider
        'slider_track': color.black,
        'slider_track_fill': color.blue_dark,
        'slider_track_disabled': color.gray_darker,
        'slider_handle': color.blue,
        'slider_handle_hovered': color.blue_light,
        'slider_handle_pressed': color.blue_dark,
        'slider_handle_disabled': color.gray_dark,

        # Channel Slider
        'channel_slider_handle': color.gray,
        'channel_slider_handle_hovered': color.gray_light,
        'channel_slider_handle_pressed': color.gray_dark,
        'channel_slider_handle_disabled': color.gray_dark,

        # Tab
        'tab': color.blue_dark,
        'tab_selected': color.blue,
        'tab_hovered': color.blue_light,
        'tab_pressed': color.blue_darker,
        'tab_disabled': color.gray_darker,

        # Combo Box
        'combo_box': color.blue,
        'combo_box_hovered': color.blue_light,
        'combo_box_text': color.gray_darkest,
        'combo_box_text_current': color.green,

        # List Box
        'list_box_header': color.gray,
        'list_box_header_disabled': color.gray_darker,
        'list_box_header_text': color.gray_darkest,
        'list_box_item_text_selected': color.gray_darkest,
        'list_box_item_text_selected_background': color.blue,
        'list_box_item_text_selected_background_disabled': color.gray_darker,
        'list_box_item_text_hovered_background': color.blue_light,
        'list_box_background': color.black,
        'list_box_background_alternate': color.gray_darkest,

        # Input
        'input_background': color.black,
        'input_outline': color.blue,
        'input_cursor': color.gray,
        'input_selection': color.gray_darker,
        'input_button': color.blue_darker,
        'input_button_hovered': color.blue_light,
        'input_button_pressed': color.blue_dark,
        'input_button_text': color.blue,
        'input_button_text_hovered': color.blue_darkest,
        'input_button_text_disabled': color.blue_darker,
        'input_button_disabled': color.blue_darkest,

        # Group box
        'group_box_header': color.gray,
        'group_box_header_hovered': color.gray_light,
        'group_box_header_pressed': color.gray_dark,
        'group_box_header_disabled': color.gray_darker,
        'group_box_header_text': color.gray_darkest,
        'group_box_background': color.gray_darkest,

        # Splitter
        'splitter': color.gray_darker,
        'splitter_hovered': color.gray_dark,
        'splitter_pressed': color.gray_darker,

        # Scroll Bar
        'scroll_bar': color.gray,
        'scroll_bar_hovered': color.gray_light,
        'scroll_bar_pressed': color.gray_dark,
        'scroll_bar_background': color.gray_darker,
        'scroll_bar_disabled': color.gray_dark,

        # Window
        'window_title_text': color.gray_darkest,
        'window_background': color.gray_darkest,
        'window_outline': color.gray,
        'window_resize_handle_hovered': color.gray_light,
        'window_close_button_pressed': color.red,
        'window_close_button_hovered': color.red_dark,

        # Menu
        'menu_background': color.blue_darkest,
        'menu_outline': color.blue,
        'menu_item_text': color.gray,
        'menu_item_text_hovered': color.blue_darkest,
        'menu_item_background_hovered': color.blue,
        'menu_item_text_disabled': color.blue_darker,
        'menu_separator': color.blue_darker,
        'menu_bar': color.blue_darkest,
    }
    _style_override: dict[str, Color] = {}

    @classmethod
    def init(cls, font: str) -> None:
        """ Initialize the GUI system. """
        if cls._initialized:
            raise RuntimeError("The GUI system has already been initialized.")

        cls._font = font
        cls._line_height = BitmapFont(font).line_height
        cls._camera = GuiCamera()

        cls._reset_textures()
        Window.add_viewport_changed_callback(cls._reset_textures)
        Renderer.add_reset_callback(cls._reset_textures)
        Renderer.add_resolution_change_callback(cls._reset_textures)

        cls._initialized = True

    @classmethod
    def check_init(cls) -> None:
        """ Check if the GUI system has been initialized. """
        # Do nothing if it's initialized
        if cls._initialized:
            return

        # Monkey patch the class functions as no-ops
        def no_op():
            return

        @contextmanager
        def no_op_context():
            if not cls._uninitialized_warning_shown:
                Log.warning("The GUI system has not been initialized; its functionality is disabled.")
                cls._uninitialized_warning_shown = True

            yield

        cls.reset = no_op
        cls.draw = no_op
        cls.context = no_op_context

    @classmethod
    @contextmanager
    def context(cls) -> Generator:
        """ Context manager for GUI operations.
        All GUI operations must take place in the context.
        """
        # Reset cursor
        cls.set_cursor(0, 0)

        # Set render target and enter context
        with Renderer.render_target(cls._texture):
            Renderer.clear()
            yield

    @classmethod
    def draw(cls) -> None:
        """ Draw the GUI pass. """
        Renderer.unset_render_target()

        # Draw main GUI texture
        Renderer.copy(
            texture=cls._texture,
            source_rect=None,
            destination_rect=cls._destination_rect,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw window layer
        Renderer.copy(
            texture=cls._window_texture,
            source_rect=None,
            destination_rect=cls._destination_rect,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw menu layer
        Renderer.copy(
            texture=cls._menu_texture,
            source_rect=None,
            destination_rect=cls._destination_rect,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw modal layer
        if cls._modal:
            Renderer.copy(
                texture=cls._modal_texture,
                source_rect=None,
                destination_rect=cls._destination_rect,
                rotation_angle=0,
                rotation_center=None,
                flip=0
            )

        # Clear render targets
        with Renderer.render_target(cls._texture):
            Renderer.clear()
        with Renderer.render_target(cls._window_texture):
            Renderer.clear()
        with Renderer.render_target(cls._menu_texture):
            Renderer.clear()
        with Renderer.render_target(cls._modal_texture):
            Renderer.clear(Color(0, 0, 0, 128))

    @classmethod
    def reset(cls) -> None:
        """ Reset the GUI pass. """

        # Delete cached items that were not used this frame
        for k in cls._widget_cache.keys() - cls._names:
            del cls._widget_cache[k]
        for k in cls._text_cache.keys() - cls._names:
            del cls._text_cache[k]
        for k in cls._data_cache.keys() - cls._names:
            del cls._data_cache[k]

        # Close open windows and menus that were not used this frame
        for w in cls._open_windows - cls._names:
            cls.close_window(w)
        for m in cls._open_menus - cls._names:
            cls.close_menu(m)

        # Clear the name list
        cls._names.clear()

        # Reset the region
        cls._region = Rect(0, 0, cls._width, cls._height)
        for stack in cls._sub_region_stack.values():
            stack.clear()
            stack.append(cls._region)

        # Clear bounding box
        cls._bbox = None

        # Update mouse info
        cls._mouse_delta = cls.mouse() - cls._previous_mouse_position
        cls._previous_mouse_position = cls.mouse()
        cls._left_mouse_pressed = Mouse.get_left_mouse_down()
        cls._left_mouse_released = Mouse.get_left_mouse_up()
        cls._mouse_scroll_wheel = Mouse.get_mouse_scroll_wheel() * MOUSE_SCROLL_SPEED

        # Close menus if the mouse was clicked
        if cls._left_mouse_pressed and not cls._mouse_is_over_menu:
            cls.close_all_menus()

        cls._mouse_is_over_menu = False

        # Update the mouse cursor
        if cls._mouse_cursor != cls._previous_mouse_cursor:
            MOUSE_CURSOR_DISPATCH[cls._mouse_cursor]()

        cls._previous_mouse_cursor = cls._mouse_cursor
        cls._mouse_cursor = MOUSE_CURSOR_ARROW

        # Update global states
        cls._current_widget = None
        cls._hovered_last_frame = cls._hovering
        cls._hovering = None
        cls._hovered_layer = LAYER_NONE
        cls._disabled = False
        cls._textures_reset = False

    @classmethod
    def camera(cls) -> Camera:
        """ Get the GUI camera. """
        return cls._camera

    @classmethod
    def zoom(cls) -> int:
        """ Get the zoom level. """
        return cls._zoom

    @classmethod
    def set_zoom(cls, zoom: int) -> None:
        """ Set the zoom level. """
        if zoom < 1:
            Log.error(f"GUI zoom must be at least 1 (got {zoom})")
            return

        cls._zoom = int(zoom)
        cls._reset_textures()

    @classmethod
    @contextmanager
    def font(cls, font: str) -> Generator:
        """ Context manager for setting the font. """
        old_font = cls._font
        cls._font = font

        old_line_height = cls._line_height
        cls._line_height = BitmapFont(font).line_height

        yield

        cls._font = old_font
        cls._line_height = old_line_height

    @classmethod
    def line_height(cls) -> int:
        """ Get the line height for the current font. """
        return cls._line_height

    @classmethod
    def style(cls, key: str) -> Color:
        """ Get a style color. """
        if override := cls._style_override.get(key):
            return override

        try:
            return cls._style[key]
        except KeyError:
            Log.error(f"Style color '{key}' does not exist")
            cls._style[key] = Color.magenta()
            return cls._style[key]

    @classmethod
    def set_style(cls, style: dict[str, Color]) -> None:
        """ Set the style. """
        # Find any missing keys in the provided style
        missing = []
        for k in cls._style.keys():
            if k not in style.keys():
                missing.append(k)

        # Error if any missing keys were found
        if missing:
            Log.error(f"Called 'gui.set_style()' with missing keys: {', '.join(missing)}")
            return

        cls._style = style

    @classmethod
    @contextmanager
    def style_override(cls, **kwargs: Color) -> Generator:
        """ Context manager to override the style. """
        old_style_override = cls._style_override
        cls._style_override = kwargs

        yield

        cls._style_override = old_style_override

    @classmethod
    def mouse(cls) -> Point:
        """ Get the mouse position. """
        return Mouse.screen_position() / cls.zoom()

    @classmethod
    def is_mouse_in_region(cls) -> bool:
        """ If True, the mouse is in the current region. """
        return cls.region().contains_point(cls.mouse())

    @classmethod
    def set_mouse_cursor(cls, cursor: int) -> None:
        """ Set the mouse cursor. """
        cls._mouse_cursor = cursor

    @classmethod
    def cursor(cls) -> Point:
        """ Get the cursor position.
        Widgets will always be created at the cursor's current position.
        After creating a widget, the cursor may be moved automatically depending on the layout.
        """
        return Point(cls._cx, cls._cy)

    @classmethod
    def set_cursor(cls, x: int, y: int) -> None:
        """ Set the cursor position. """
        cls._cx = int(x)
        cls._cy = int(y)

    @classmethod
    def save_cursor(cls) -> None:
        """ Save the cursor position to the stack. """
        cls._cursor_stack.append(cls.cursor())

    @classmethod
    def restore_cursor(cls) -> None:
        """ Restore the most recently saved cursor position. """
        cls.set_cursor(*cls._cursor_stack.pop())

    @classmethod
    def disabled(cls) -> bool:
        """ If True, the widget interaction state is disabled. """
        # If a modal window is present, disable if we're not currently in the window
        if cls._modal:
            if cls._window_stack and cls._window_stack[-1] == cls._modal:
                return cls._disabled
            return True

        return cls._disabled

    @classmethod
    def disable(cls) -> None:
        """ Set the widget interaction state to disabled. """
        cls._disabled = True

    @classmethod
    def enable(cls) -> None:
        """ Set the widget interaction state to enabled. """
        cls._disabled = False

    @classmethod
    def region(cls) -> Rect:
        """ The current region rect. """
        if cls._layer_sub_region_stack():
            return cls._layer_sub_region_stack()[-1]
        else:
            return cls._region

    @classmethod
    def pad(cls, size: int) -> None:
        """ Add padding to the current region. """
        if cls._layer_sub_region_stack():
            cls._cx += size
            cls._cy += size
            r = cls.region()
            cls._layer_sub_region_stack()[-1] = Rect(
                r.x + size,
                r.y + size,
                r.width - size * 2,
                r.height - size * 2,
            )
            cls._set_region_clip_rect()

    @classmethod
    def start_sub_region(cls, rect: Rect) -> None:
        """ Start a sub-region. """
        cls._layer_sub_region_stack().append(rect)

        # Set clip rect
        cls._set_region_clip_rect()

        # Update the cursor
        cls.save_cursor()
        cls.set_cursor(rect.x, rect.y)

    @classmethod
    def end_sub_region(cls) -> None:
        """ End the current sub-region. """
        cls._layer_sub_region_stack().pop()

        # Restore the previous clip rect
        cls._set_region_clip_rect()

        # Restore the cursor
        cls.restore_cursor()

    @classmethod
    @contextmanager
    def sub_region(cls, rect: Rect) -> Generator:
        """ Sub-region context manager. """
        cls.start_sub_region(rect)
        yield
        cls.end_sub_region()

    @classmethod
    def available_x(cls) -> int:
        """ The amount of space available to the right of the cursor, in the current region. """
        available = cls.region().right() - cls._cx + 1
        if available < 0:
            available = 0
        return available

    @classmethod
    def available_y(cls) -> int:
        """ The amount of space available below the cursor, in the current region. """
        available = cls.region().bottom() - cls._cy + 1
        if available < 0:
            available = 0
        return available

    @classmethod
    def available_rect(cls) -> Rect:
        """ The amount of available space left in the current region. """
        return Rect(cls._cx, cls._cy, cls.available_x(), cls.available_y())

    @classmethod
    @contextmanager
    def x_spacing(cls, spacing: int) -> Generator:
        """ Context manager for setting the x-spacing. """
        old_x_spacing = cls._spacing_x
        cls._spacing_x = spacing

        yield

        cls._spacing_x = old_x_spacing

    @classmethod
    @contextmanager
    def y_spacing(cls, spacing: int) -> Generator:
        """ Context manager for setting the y-spacing. """
        old_y_spacing = cls._spacing_y
        cls._spacing_y = spacing

        yield

        cls._spacing_y = old_y_spacing

    @classmethod
    def layout(cls) -> int:
        """ Get the current layout.
        If no layout is on the stack, it will default to a vertical layout.
        """
        if cls._layout_stack:
            return cls._layout_stack[-1]
        else:
            return LAYOUT_VERTICAL

    @classmethod
    def start_layout(cls, layout: int) -> None:
        """ Start a layout. """
        cls._layout_stack.append(layout)

    @classmethod
    def end_layout(cls) -> None:
        """ End the current layout """
        cls._layout_stack.pop()

    @classmethod
    @contextmanager
    def vertical_layout(cls) -> Generator:
        """ Vertical layout. """
        cls.start_layout(LAYOUT_VERTICAL)
        cls.start_bbox()
        yield
        cls.end_bbox()
        cls.end_layout()
        if cls.bbox():
            cls._update_cursor_after_placement(cls.bbox())

    @classmethod
    @contextmanager
    def horizontal_layout(cls) -> Generator:
        """ Horizontal layout. """
        cls.start_layout(LAYOUT_HORIZONTAL)
        cls.start_bbox()
        yield
        cls.end_bbox()
        cls.end_layout()
        if cls.bbox():
            cls._update_cursor_after_placement(cls.bbox())

    @classmethod
    @contextmanager
    def grid_layout(cls, columns: int, column_width: int, row_height: int) -> Generator:
        """ Grid layout. """
        old_grid_columns = cls._grid_columns
        old_grid_x = cls._grid_x
        old_grid_y = cls._grid_y
        old_grid_column_width = cls._grid_column_width
        old_grid_row_height = cls._grid_row_height
        old_grid_index = cls._grid_index

        cls._grid_columns = columns
        cls._grid_x = cls._cx
        cls._grid_y = cls._cy
        cls._grid_column_width = column_width
        cls._grid_row_height = row_height
        cls._grid_index = 0

        cls.start_layout(LAYOUT_GRID)
        cls.start_bbox()
        yield
        cls.end_bbox()
        cls.end_layout()
        if cls.bbox():
            cls._update_cursor_after_placement(cls.bbox())

        cls._grid_columns = old_grid_columns
        cls._grid_x = old_grid_x
        cls._grid_y = old_grid_y
        cls._grid_column_width = old_grid_column_width
        cls._grid_row_height = old_grid_row_height
        cls._grid_index = old_grid_index

    @classmethod
    def start_bbox(cls) -> None:
        """ Start a bounding box calculation. """
        cls._bbox_stack.append(None)
        cls._calculating_bbox = True

    @classmethod
    def end_bbox(cls) -> None:
        """ End the current bounding box calculation. """
        bbox = cls._bbox_stack.pop()

        if not cls._bbox_stack:
            cls._calculating_bbox = False

        # If bbox is None, then no widgets were placed
        if not bbox:
            cls._bbox = None
            return

        # Calculate and set the bounding box
        x_min, x_max, y_min, y_max = bbox
        width = x_max - x_min + 1
        height = y_max - y_min + 1
        cls._bbox = Rect(x_min, y_min, width, height)

    @classmethod
    def bbox(cls) -> Rect | None:
        """ Returns the last bounding box calculated. """
        return cls._bbox

    @classmethod
    @contextmanager
    def no_bbox(cls) -> Generator:
        """ Create widgets without updating the current bounding box calculation. """
        old_calculating_bbox = cls._calculating_bbox
        old_bbox_stack = cls._bbox_stack

        cls._bbox_stack = deque()
        cls._calculating_bbox = False

        yield

        cls._bbox_stack = old_bbox_stack
        cls._calculating_bbox = old_calculating_bbox

    @classmethod
    def splitter(cls,
                 name: str,
                 rect: Rect,
                 size: int,
                 splitter_range: tuple[int, int] | None,
                 direction: int
                 ) -> tuple[Rect, Rect]:
        """ Split a rect into 2 rects.
        Example usage:
        ```
        with gui.context():
            rect = gui.available_rect()
            size = 100
            a, b = gui.splitter("Splitter", rect, size, None, SPLIT_LEFT)
            with gui.sub_region(a):
                pass
            with gui.sub_region(b):
                pass
        ```
        """
        # Store the cursor position
        cls.save_cursor()

        # Get cached size
        data = cls.cached_data(name, size=size)
        size = data['size']

        # Account for splitter
        if splitter_range:
            spacing = SPLITTER_THICKNESS + 2
        else:
            spacing = 0

        # Calculate rects
        if direction == SPLIT_LEFT:
            split_region_x = rect.x
            split_region_y = rect.y
            split_region_w = size
            split_region_h = rect.height

            remainder_x = rect.x + split_region_w + spacing
            remainder_y = rect.y
            remainder_w = rect.width - (split_region_w + spacing) - 1
            remainder_h = rect.height

            splitter_x = split_region_x + split_region_w + 1
            splitter_y = split_region_y + (split_region_h // 2) - (SPLITTER_LENGTH // 2)
            splitter_w = SPLITTER_THICKNESS
            splitter_h = SPLITTER_LENGTH

        elif direction == SPLIT_RIGHT:
            split_region_x = rect.x + rect.width - size
            split_region_y = rect.y
            split_region_w = size
            split_region_h = rect.height

            remainder_x = rect.x
            remainder_y = rect.y
            remainder_w = rect.width - (split_region_w + spacing)
            remainder_h = rect.height

            splitter_x = remainder_x + remainder_w + 1
            splitter_y = split_region_y + (split_region_h // 2) - (SPLITTER_LENGTH // 2)
            splitter_w = SPLITTER_THICKNESS
            splitter_h = SPLITTER_LENGTH

        elif direction == SPLIT_TOP:
            split_region_x = rect.x
            split_region_y = rect.y
            split_region_w = rect.width
            split_region_h = size

            remainder_x = rect.x
            remainder_y = rect.y + split_region_h + spacing
            remainder_w = rect.width
            remainder_h = rect.height - (split_region_h + spacing) - 1

            splitter_x = split_region_x + (split_region_w // 2) - (SPLITTER_LENGTH // 2)
            splitter_y = split_region_y + split_region_h + 1
            splitter_w = SPLITTER_LENGTH
            splitter_h = SPLITTER_THICKNESS

        elif direction == SPLIT_BOTTOM:
            split_region_x = rect.x
            split_region_y = rect.y + rect.height - size
            split_region_w = rect.width
            split_region_h = size

            remainder_x = rect.x
            remainder_y = rect.y
            remainder_w = rect.width
            remainder_h = rect.height - (split_region_h + spacing)

            splitter_x = remainder_x + (split_region_w // 2) - (SPLITTER_LENGTH // 2)
            splitter_y = remainder_y + remainder_h + 1
            splitter_w = SPLITTER_LENGTH
            splitter_h = SPLITTER_THICKNESS

        else:
            Log.error(f"Split direction {direction} is invalid")
            return Rect.empty(), Rect.empty()

        split_region_rect = Rect(split_region_x, split_region_y, split_region_w, split_region_h)
        remainder_rect = Rect(remainder_x, remainder_y, remainder_w, remainder_h)

        # Create splitter widget
        if splitter_range:
            cls.set_cursor(splitter_x, splitter_y)
            widget = cls.widget(f"{name}", splitter_w, splitter_h)

            # Splitter color
            if widget['held'] or widget['dragged']:
                color = cls.style("splitter_pressed")
            elif widget['hovered']:
                color = cls.style("splitter_hovered")
            else:
                color = cls.style("splitter")

            # Draw splitter
            if direction == SPLIT_LEFT or direction == SPLIT_RIGHT:
                widget['rect'].left_line().draw(cls._camera, color)
                widget['rect'].right_line().draw(cls._camera, color)
            else:
                widget['rect'].top_line().draw(cls._camera, color)
                widget['rect'].bottom_line().draw(cls._camera, color)

            # Change splitter size if the widget is dragged
            if widget['dragged']:
                if direction == SPLIT_LEFT:
                    size = (widget['drag_start'].x + cls._mouse_drag_delta.x) - split_region_x
                elif direction == SPLIT_RIGHT:
                    size = rect.right() - (widget['drag_start'].x + cls._mouse_drag_delta.x) - splitter_w
                elif direction == SPLIT_TOP:
                    size = (widget['drag_start'].y + cls._mouse_drag_delta.y) - split_region_y
                elif direction == SPLIT_BOTTOM:
                    size = rect.bottom() - (widget['drag_start'].y + cls._mouse_drag_delta.y) - splitter_h

            # Clamp size to range
            size = pmath.clamp(size, splitter_range[0], splitter_range[1])

            # Update mouse cursor
            if widget['hovered'] or widget['dragged']:
                if direction == SPLIT_LEFT or direction == SPLIT_RIGHT:
                    cls.set_mouse_cursor(MOUSE_CURSOR_RESIZE_HORIZONTAL)
                else:
                    cls.set_mouse_cursor(MOUSE_CURSOR_RESIZE_VERTICAL)

        # Cache the size
        data['size'] = size

        # Restore the cursor
        cls.restore_cursor()

        # Return the split rects
        return split_region_rect, remainder_rect

    @classmethod
    def split_left(cls,
                   name: str,
                   rect: Rect,
                   width: int,
                   splitter_range: tuple[int, int] | None = None
                   ) -> tuple[Rect, Rect]:
        """ Split a rect into left and right sub-rects.
        Width controls the left rect's width, and the range is the minimum/maximum width of the left rect.
        Returns a tuple of (left_rect, right_rect)
        """
        return cls.splitter(name, rect, width, splitter_range, SPLIT_LEFT)

    @classmethod
    def split_right(cls,
                    name: str,
                    rect: Rect,
                    width: int,
                    splitter_range: tuple[int, int] | None = None
                    ) -> tuple[Rect, Rect]:
        """ Split a rect into right and left sub-rects.
        Width controls the right rect's width, and the range is the minimum/maximum width of the right rect.
        Returns a tuple of (right_rect, left_rect)
        """
        return cls.splitter(name, rect, width, splitter_range, SPLIT_RIGHT)

    @classmethod
    def split_top(cls,
                  name: str,
                  rect: Rect,
                  height: int,
                  splitter_range: tuple[int, int] | None = None
                  ) -> tuple[Rect, Rect]:
        """ Split a rect into top and bottom sub-rects.
        Height controls the top rect's height, and the range is the minimum/maximum height of the top rect.
        Returns a tuple of (top_rect, bottom_rect)
        """
        return cls.splitter(name, rect, height, splitter_range, SPLIT_TOP)

    @classmethod
    def split_bottom(cls,
                     name: str,
                     rect: Rect,
                     height: int,
                     splitter_range: tuple[int, int] | None = None
                     ) -> tuple[Rect, Rect]:
        """ Split a rect into bottom and top sub-rects.
        Height controls the bottom rect's height, and the range is the minimum/maximum height of the bottom rect.
        Returns a tuple of (bottom_rect, top_rect)
        """
        return cls.splitter(name, rect, height, splitter_range, SPLIT_BOTTOM)

    @classmethod
    def outline(cls, radius: int = BOX_RADIUS) -> None:
        """ Add an outline to the current region. """
        if radius < 1:
            Renderer.draw_rect_outline(cls.available_rect(), cls.style("outline"))
        else:
            Renderer.draw_rounded_rect_outline(cls.available_rect(), radius, cls.style("outline"))

    @classmethod
    def background(cls, radius: int = BOX_RADIUS) -> None:
        """ Add a background to the current region. """
        if radius < 1:
            Renderer.draw_rect_solid(cls.available_rect(), cls.style("background"))
        else:
            Renderer.draw_rounded_rect_solid(cls.available_rect(), radius, cls.style("background"))

    @classmethod
    def current(cls) -> Widget | None:
        """ Returns the widget that was just created. """
        return cls._widget_cache.get(cls._current_widget)

    @classmethod
    def widget(cls, name: str, width: int, height: int) -> Widget:
        """ Base widget creation. """
        # Register the widget name
        cls._register_name(name)

        # Get widget from cache, or create new
        widget = cls._widget_cache.get(name)
        if not widget:
            widget = Widget(
                name=name,
                rect=Rect.empty(),
                hovered=False,
                pressed=False,
                held=False,
                dragged=False,
                drag_start=Point.zero(),
                released=False,
                clicked=False,
            )
            cls._widget_cache[name] = widget

        # Update geometry
        widget['rect'] = Rect(cls._cx, cls._cy, width, height)

        # Check if the mouse is over the widget
        mouse_is_over_widget = False
        if widget['rect'].contains_point(cls.mouse()) and cls.is_mouse_in_region():
            mouse_is_over_widget = True

        # Now we do some dumb logic because menus (which are drawn over everything else) need to be prioritized.
        # So if the current hovered item is a menu, we only consider the mouse over this widget if it's also in a menu.
        if cls._layer() < cls._hovered_layer:
            mouse_is_over_widget = False

        # Update state
        widget['hovered'] = False
        widget['pressed'] = False
        widget['released'] = False
        widget['clicked'] = False

        if not cls.disabled():
            # Check for hover state
            if mouse_is_over_widget and name == cls._hovered_last_frame:
                widget['hovered'] = True

            # Check for press and held states
            if widget['hovered']:
                if cls._left_mouse_pressed:
                    widget['pressed'] = True
                    widget['held'] = True
                    cls._mouse_drag_start = cls.mouse()

            # Check for drag state
            if widget['held']:
                if cls._mouse_delta.x or cls._mouse_delta.y:
                    if not widget['dragged']:
                        widget['dragged'] = True
                        widget['drag_start'] = widget['rect'].position()
                    cls._mouse_drag_delta = cls.mouse() - cls._mouse_drag_start

            # Check for release and clicked states
            if cls._left_mouse_released:
                if widget['held']:
                    widget['released'] = True
                    if widget['hovered']:
                        widget['clicked'] = True
                widget['held'] = False
                widget['dragged'] = False
                cls._mouse_drag_start = Point.zero()
                cls._mouse_drag_delta = Point.zero()

        # Track global hover state
        # This is done *after* checking the widget state, it couldn't be globally unique with overlapping UI elements.
        # This does introduce a one-frame delay to the widget's hover state checking.
        if mouse_is_over_widget:
            cls._hovering = name
            if cls._layer() > cls._hovered_layer:
                cls._hovered_layer = cls._layer()

        # Update the cursor
        cls._update_cursor_after_placement(widget['rect'])

        # Update the current widget
        cls._current_widget = name

        return widget

    @classmethod
    def spacer(cls, *, width: int | None = None, height: int | None = None) -> None:
        """ Create a spacer. """
        if width is None:
            width = cls._spacing_x
        if height is None:
            height = cls._spacing_y
        cls._update_cursor_after_placement(Rect(cls._cx, cls._cy, width, height))

    @classmethod
    def horizontal_line(cls, width: int) -> None:
        """ Create a horizontal line widget. """
        a = cls.cursor()
        b = cls.cursor() + Point(width, 0)
        line = Line(a, b)
        line.draw(cls._camera, cls.style("line"))

        rect = Rect(cls.cursor().x, cls.cursor().y, width, 1)
        cls._update_cursor_after_placement(rect)

    @classmethod
    def vertical_line(cls, height: int) -> None:
        """ Create a vertical line widget. """
        a = cls.cursor()
        b = cls.cursor() + Point(0, height)
        line = Line(a, b)
        line.draw(cls._camera, cls.style("line"))

        rect = Rect(cls.cursor().x, cls.cursor().y, 1, height)
        cls._update_cursor_after_placement(rect)

    @classmethod
    def rect(cls, width: int, height: int, color: Color, solid: bool = False) -> None:
        """ Create a rectangle widget. """
        rect = Rect(cls._cx, cls._cy, width, height)
        rect.draw(cls._camera, color, solid)
        cls._update_cursor_after_placement(rect)

    @classmethod
    def text(cls, name: str) -> None:
        """ Create a text widget. """
        text = cls.cached_text(name)

        if cls.disabled():
            text.color = cls.style("text_disabled")
        else:
            text.color = cls.style("text")

        # Create widget
        widget = cls.widget(name, text.width, text.height)
        text.draw(cls._camera, widget['rect'].position())

    @classmethod
    @contextmanager
    def label(cls, name: str, width: int = 0) -> Generator:
        """ Lay out widgets with a label. """
        with cls.horizontal_layout():
            # Get label text
            text = cls.cached_text(name)

            if cls.disabled():
                text.color = cls.style("text_disabled")
            else:
                text.color = cls.style("label")

            # Create label widget
            widget = cls.widget(name, text.width, text.height)
            text.draw(cls._camera, widget['rect'].position())

            # Add spacing after the text to match the width
            if width:
                label_width = width - cls.current()['rect'].width
            else:
                label_width = LABEL_WIDTH - cls.current()['rect'].width
            if label_width > 0:
                cls.spacer(width=label_width, height=0)

            with cls.vertical_layout():
                yield

    @classmethod
    def hyperlink(cls, name: str) -> bool:
        """ Create a hyperlink text widget.
        Returns True if the hyperlink was clicked.
        """
        text = cls.cached_text(name)

        # Create widget
        widget = cls.widget(name, text.width, text.height + 1)

        # Widget color
        if cls.disabled():
            color = cls.style("text_disabled")
        elif widget['hovered'] and widget['held']:
            color = cls.style("url_pressed")
        elif widget['hovered']:
            color = cls.style("url_hovered")
        else:
            color = cls.style("url")

        text.color = color

        # Draw text
        text.draw(cls._camera, widget['rect'].position())

        # Draw underline
        p0 = Point(widget['rect'].left(), widget['rect'].bottom())
        p1 = Point(widget['rect'].right(), widget['rect'].bottom())
        Line(p0, p1).draw(cls._camera, color)

        # Update mouse cursor
        if widget['hovered']:
            cls.set_mouse_cursor(MOUSE_CURSOR_HAND)

        return widget['clicked']

    @classmethod
    def sprite(cls, name: str, sprite: Sprite) -> None:
        """ Create a sprite widget. """
        widget = cls.widget(name, sprite.width(), sprite.height())

        if cls.disabled():
            sprite.opacity = 128
        else:
            sprite.opacity = 255

        sprite.draw(cls._camera, widget['rect'].position())

    @classmethod
    def button(cls, name: str) -> bool:
        """ Create a button widget with text.
        Returns True if the button was clicked.
        """
        text = cls.cached_text(name)
        text.color = cls.style("button_text")

        # Calculate size
        width, height = cls._button_size(text, None)

        # Create widget
        widget = cls._button(name, width, height)
        button_rect, shadow_rect = cls._button_rects(widget)
        color = cls._button_color(widget)

        # Draw background and shadow
        Renderer.draw_rounded_rect_solid(shadow_rect, BUTTON_RADIUS, cls.style("button_shadow"))
        Renderer.draw_rounded_rect_solid(button_rect, BUTTON_RADIUS, color)

        # Draw text
        text_position, _ = cls._button_content_positions(widget, text, None)
        text.draw(cls._camera, text_position)

        return widget['clicked']

    @classmethod
    def sprite_button(cls, name: str, sprite: Sprite) -> bool:
        """ Create a button widget with a sprite and text.
        Returns True if the button was clicked.
        """
        if name.startswith("##"):
            text = None
        else:
            text = cls.cached_text(name)
            text.color = cls.style("button_text")

        # Sprite color
        if cls.disabled():
            sprite.opacity = 128
        else:
            sprite.opacity = 255

        # Create widget
        width, height = cls._button_size(text, sprite)
        widget = cls._button(name, width, height)
        button_rect, shadow_rect = cls._button_rects(widget)
        color = cls._button_color(widget)

        # Draw background and shadow
        Renderer.draw_rounded_rect_solid(shadow_rect, BUTTON_RADIUS, cls.style("button_shadow"))
        Renderer.draw_rounded_rect_solid(button_rect, BUTTON_RADIUS, color)

        # Draw sprite and text
        text_position, sprite_position = cls._button_content_positions(widget, text, sprite)
        sprite.draw(cls._camera, sprite_position)
        if text:
            text.draw(cls._camera, text_position)

        return widget['clicked']

    @classmethod
    def color_button(cls, name: str, color: Color) -> Color:
        """ Create a color button widget that shows a color dialog. """
        # Create widget
        widget = cls._button(name, COLOR_BUTTON_WIDTH, COLOR_BUTTON_HEIGHT)
        button_rect, shadow_rect = cls._button_rects(widget)
        color_preview_rect = Rect(button_rect.x + 1, button_rect.y + 1, button_rect.width - 2, button_rect.height - 2)

        # Button color
        if cls.disabled():
            button_color = cls.style("color_button_disabled")
        elif widget['held'] or widget['dragged']:
            button_color = cls.style("color_button_pressed")
        elif widget['hovered']:
            button_color = cls.style("color_button_hovered")
        else:
            button_color = cls.style("color_button")

        # Get cached data
        data = cls.cached_data(name, dialog_color=None, tab=1)
        if cls._textures_reset:
            data['checkerboard'] = cls._transparent_checkerboard_texture(
                color_preview_rect.width,
                color_preview_rect.height
            )

        # Draw background and shadow
        Renderer.draw_rounded_rect_solid(shadow_rect, COLOR_BUTTON_RADIUS, cls.style("button_shadow"))
        Renderer.draw_rounded_rect_solid(button_rect, COLOR_BUTTON_RADIUS, button_color)

        # Draw the color preview
        Renderer.copy(
            texture=data['checkerboard'],
            source_rect=None,
            destination_rect=color_preview_rect,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )
        color_preview_rect.draw(cls._camera, color, solid=True)

        # Open the dialog if the button was clicked
        window_name = f"Pick a Color##__{name}"
        if widget['clicked']:
            data['dialog_color'] = Color(color.r, color.g, color.b, color.a)
            cls.open_window(f"Pick a Color##__{name}", (230, 145), modal=True)

        with cls.no_bbox():
            if cls.window(window_name):
                # Get dialog data from cache
                c = data['dialog_color']
                tab = data['tab']

                # Tabs
                cls.pad(4)
                tab = cls.tabs(f"{name}__Tabs", tab, ["RGB", "HSV"])

                with cls.horizontal_layout():
                    # Color box
                    with cls.vertical_layout():
                        color_box_size = 50
                        c = cls.color_box(f"{name}__ColorBox", color_box_size, color_box_size, c)
                        c = cls.hue_ribbon(f"{name}__HueRibbon", color_box_size, 7, c)
                        c = cls.alpha_ribbon(f"{name}__AlphaRibbon", color_box_size, 7, c)

                        cls.spacer()

                    # Sliders
                    if tab == 0:
                        c = cls.rgba_sliders(f"{name}__RGBASliders", 100, c)
                    else:
                        c = cls.hsva_sliders(f"{name}__HSVASliders", 100, c)

                # Button row
                with cls.horizontal_layout():
                    cls.start_bbox()
                    with cls.x_spacing(0):
                        cls.color_preview(f"{name}__Current", color_box_size // 2, 16, color)
                    cls.color_preview(f"{name}__New", color_box_size // 2, 16, c)
                    cls.end_bbox()
                    cls.bbox().draw(cls._camera, cls.style("line"))
                    c = cls.hex_color_input(f"{name}__Hex", cls.available_x() - 100, c)
                    if cls.button(f"Ok##__{name}"):
                        color = c
                        cls.close_window(window_name)
                    if cls.button(f"Cancel##__{name}"):
                        cls.close_window(window_name)

                # Cache dialog data
                data['dialog_color'] = c
                data['tab'] = tab

                cls.end_window()

        return color

    @classmethod
    def button_group(cls, name: str, current_index: int, labels: list[str]) -> int:
        """ Create a button group.
        Returns the index of the selected button.
        """
        if len(labels) < 2:
            Log.error(f"Button group '{name}' must include at least 2 labels")
            return current_index

        # Get text for labels
        text_list = cls.cached_text_list(labels, suffix=f"{name}__Label")
        for text in text_list:
            text.color = cls.style("button_text")

        # Calculate button size
        button_widths = []
        button_height = 0
        for text in text_list:
            w, h = cls._button_size(text, None)
            button_widths.append(w)
            if h > button_height:
                button_height = h

        # Calculate group size
        group_x = cls._cx
        group_y = cls._cy + BUTTON_DEPTH
        group_width = sum(button_widths) + BUTTON_GROUP_SPACING * (len(labels) - 1)
        group_height = button_height

        # Draw shadow rect for group
        shadow_rect = Rect(group_x, group_y, group_width, group_height)
        Renderer.draw_rounded_rect_solid(shadow_rect, BUTTON_RADIUS, cls.style("button_shadow"))

        # Create buttons
        with cls.horizontal_layout():
            with cls.x_spacing(BUTTON_GROUP_SPACING):
                for i, label in enumerate(labels):
                    # Create widget
                    button_width = button_widths[i]
                    widget = cls._button(f"{name}__{i}", button_width, button_height)
                    button_rect, shadow_rect = cls._button_rects(widget)
                    color = cls._button_color(widget)

                    # Get text
                    text = text_list[i]
                    text_position, _ = cls._button_content_positions(widget, text, None)

                    # Update selection
                    if widget['clicked']:
                        current_index = i

                    # Update color and position if button is selected
                    if i == current_index:
                        if cls.disabled():
                            color = cls.style("button_disabled")
                        else:
                            color = cls.style("button_pressed")
                        text_position += Point(0, shadow_rect.y - button_rect.y)
                        button_rect = shadow_rect

                    # Corners
                    if i == 0:
                        corners = (True, False, True, False)
                    elif i == len(labels) - 1:
                        corners = (False, True, False, True)
                    else:
                        corners = (False, False, False, False)

                    # Draw background
                    Renderer.draw_rect_with_optional_rounded_corners_solid(button_rect, BUTTON_RADIUS, *corners, color)

                    # Draw text
                    text.draw(cls._camera, text_position)

        return current_index

    @classmethod
    def sprite_button_group(cls,
                            name: str,
                            current_index: int,
                            sprites: list[Sprite],
                            labels: list[str] | None = None
                            ) -> int:
        """ Create a sprite button group.
        Returns the index of the selected button.
        """
        if len(sprites) < 2:
            Log.error(f"Sprite button group '{name}' must include at least 2 sprites")
            return current_index

        if labels:
            if len(sprites) != len(labels):
                Log.error(f"Sprite button group '{name}' must have the same number of sprites and labels")
                return current_index

        # Get text for labels
        if labels:
            text_list = cls.cached_text_list(labels, suffix=f"{name}__Label")
            for text in text_list:
                text.color = cls.style("button_text")

        # Calculate button size
        button_widths = []
        button_height = 0
        for i, sprite in enumerate(sprites):
            if labels:
                text = text_list[i]
            else:
                text = None

            w, h = cls._button_size(text, sprite)
            button_widths.append(w)
            if h > button_height:
                button_height = h

        # Calculate group size
        group_x = cls._cx
        group_y = cls._cy + BUTTON_DEPTH
        group_width = sum(button_widths) + BUTTON_GROUP_SPACING * (len(sprites) - 1)
        group_height = button_height

        # Draw shadow rect for group
        shadow_rect = Rect(group_x, group_y, group_width, group_height)
        Renderer.draw_rounded_rect_solid(shadow_rect, BUTTON_RADIUS, cls.style("button_shadow"))

        # Create buttons
        with cls.horizontal_layout():
            with cls.x_spacing(BUTTON_GROUP_SPACING):
                for i, sprite in enumerate(sprites):
                    # Get text
                    if labels:
                        text = text_list[i]
                    else:
                        text = None

                    # Create widget
                    button_width = button_widths[i]
                    widget = cls._button(f"{name}__{i}", button_width, button_height)
                    button_rect, shadow_rect = cls._button_rects(widget)
                    color = cls._button_color(widget)

                    # Get positions
                    text_position, sprite_position = cls._button_content_positions(widget, text, sprite)

                    # Update selection
                    if widget['clicked']:
                        current_index = i

                    # Update color and positions if button is selected
                    if i == current_index:
                        if cls.disabled():
                            color = cls.style("button_disabled")
                        else:
                            color = cls.style("button_pressed")
                        text_position += Point(0, shadow_rect.y - button_rect.y)
                        sprite_position += Point(0, shadow_rect.y - button_rect.y)
                        button_rect = shadow_rect

                    # Corners
                    if i == 0:
                        corners = (True, False, True, False)
                    elif i == len(sprites) - 1:
                        corners = (False, True, False, True)
                    else:
                        corners = (False, False, False, False)

                    # Draw background
                    Renderer.draw_rect_with_optional_rounded_corners_solid(button_rect, BUTTON_RADIUS, *corners, color)

                    # Draw sprite and text
                    sprite.draw(cls._camera, sprite_position)
                    if text:
                        text.draw(cls._camera, text_position)

        return current_index

    @classmethod
    def checkbox(cls, name: str, checked: bool) -> bool:
        """ Create a checkbox.
        Returns True if the checkbox is checked.
        """
        # Create widget
        widget = cls.widget(name, CHECKBOX_SIZE, CHECKBOX_SIZE)

        # Toggle on click
        if widget['clicked']:
            checked = not checked

        # Checkbox color
        if widget['hovered']:
            color = cls.style("checkbox_hovered")
        else:
            if checked:
                if cls.disabled():
                    color = cls.style("checkbox_on_disabled")
                else:
                    color = cls.style("checkbox_on")
            else:
                color = cls.style("checkbox_off")

        # Draw checkbox
        Renderer.draw_rounded_rect_solid(widget['rect'], CHECKBOX_RADIUS, color)

        # Draw checkmark
        if checked:
            p0 = CHECKBOX_CHECKMARK_P0 + widget['rect'].position()
            p1 = CHECKBOX_CHECKMARK_P1 + widget['rect'].position()
            p2 = CHECKBOX_CHECKMARK_P2 + widget['rect'].position()
            Renderer.draw_thick_line(Line(p0, p1), CHECKBOX_RADIUS, cls.style("checkbox_checkmark"))
            Renderer.draw_thick_line(Line(p1, p2), CHECKBOX_RADIUS, cls.style("checkbox_checkmark"))

        return checked

    @classmethod
    def toggle(cls, name: str, on: bool) -> bool:
        """ Create a toggle switch widget.
        Returns True if the toggle switch is on.
        """
        # Create widget
        widget = cls.widget(name, TOGGLE_SWITCH_WIDTH, TOGGLE_SWITCH_HEIGHT)

        # Toggle on click
        if widget['clicked']:
            on = not on

        # Color
        if cls.disabled():
            handle_color = cls.style("toggle_handle_disabled")
        elif widget['held'] or widget['dragged']:
            handle_color = cls.style("toggle_handle_pressed")
        elif widget['hovered']:
            handle_color = cls.style("toggle_handle_hovered")
        else:
            handle_color = cls.style("toggle_handle")

        if on:
            if cls.disabled():
                track_color = cls.style("toggle_track_fill_disabled")
            else:
                track_color = cls.style("toggle_track_fill")
        else:
            track_color = cls.style("toggle_track")

        # Draw track
        Renderer.draw_rounded_rect_solid(widget['rect'], TOGGLE_SWITCH_RADIUS, track_color)

        # Draw handle
        handle_x = widget['rect'].x + 1
        handle_y = widget['rect'].y + 1
        if on:
            handle_x += TOGGLE_SWITCH_WIDTH - TOGGLE_SWITCH_HANDLE_SIZE - 2

        handle_rect = Rect(handle_x, handle_y, TOGGLE_SWITCH_HANDLE_SIZE, TOGGLE_SWITCH_HANDLE_SIZE)
        Renderer.draw_rounded_rect_solid(handle_rect, TOGGLE_SWITCH_HANDLE_RADIUS, handle_color)

        return on

    @classmethod
    def slider(cls, name: str, width: int, value: float, minimum: float, maximum: float) -> float:
        """ Create a slider widget.
        Returns the new value.
        """
        # Create widget
        widget = cls._slider(name, width)

        # Color
        if cls.disabled():
            handle_color = cls.style("slider_handle_disabled")
            slider_track_fill_color = cls.style("slider_track_disabled")
        else:
            slider_track_fill_color = cls.style("slider_track_fill")
            if widget['held'] or widget['dragged']:
                handle_color = cls.style("slider_handle_pressed")
            elif widget['hovered']:
                handle_color = cls.style("slider_handle_hovered")
            else:
                handle_color = cls.style("slider_handle")

        # Calculate current percentage
        percent = pmath.remap(value, minimum, maximum, 0.0, 1.0)

        # Calculate geometry
        handle_rect = cls._slider_handle_rect(widget, percent)
        track_rect, fill_rect = cls._slider_track_rects(widget, percent)

        # Draw track
        track_rect.draw(cls._camera, cls.style("slider_track"), solid=True)
        fill_rect.draw(cls._camera, slider_track_fill_color, solid=True)

        # Draw handle
        Renderer.draw_rounded_rect_solid(handle_rect, SLIDER_HANDLE_RADIUS, handle_color)

        # Drag
        if widget['held']:
            value = cls._slider_drag_value(widget, minimum, maximum)

        return value

    @classmethod
    def int_slider(cls, name: str, width: int, value: int, minimum: int, maximum: int) -> int:
        """ Create a slider widget for integer values. """
        return int(cls.slider(name, width, value, minimum, maximum))

    @classmethod
    def tabs(cls, name: str, current_index: int, labels: list[str]) -> int:
        """ Create a tab group. """
        if len(labels) < 1:
            Log.error(f"Button group '{name}' must include at least 1 label")
            return current_index

        # Get text for labels
        text_list = cls.cached_text_list(labels, suffix=f"{name}__Label")
        for text in text_list:
            text.color = cls.style("button_text")

        # Create tabs
        with cls.horizontal_layout():
            with cls.x_spacing(TAB_SPACING):
                cls.spacer(width=TAB_SPACING, height=0)
                for i, label in enumerate(labels):
                    # Get text
                    text = text_list[i]

                    # Calculate size
                    width = text.width + TAB_X_PADDING * 2
                    height = text.height + TAB_Y_PADDING * 2

                    # Create widget
                    widget = cls._button(f"{name}__{i}", width, height)
                    rect = widget['rect']

                    # Update selection
                    if widget['clicked']:
                        current_index = i

                    # Color
                    line_color = cls.style("tab_selected")
                    if cls.disabled():
                        tab_color = cls.style("tab_disabled")
                        line_color = cls.style("tab_disabled")
                    elif widget['hovered']:
                        tab_color = cls.style("tab_hovered")
                    elif i == current_index:
                        tab_color = cls.style("tab_selected")
                    elif widget['held'] or widget['dragged']:
                        tab_color = cls.style("tab_pressed")
                    else:
                        tab_color = cls.style("tab")

                    # Corners
                    corners = (True, True, False, False)

                    # Draw tab
                    Renderer.draw_rect_with_optional_rounded_corners_solid(rect, TAB_RADIUS, *corners, tab_color)

                    # Draw text
                    text_position = rect.position() + Point(TAB_X_PADDING, TAB_Y_PADDING)
                    text.draw(cls._camera, text_position)

        # Draw line
        left = cls.bbox().x
        right = left + cls.available_x()
        a = Point(left, cls.bbox().bottom())
        b = Point(right, cls.bbox().bottom())
        Line(a, b).draw(cls._camera, line_color)

        return current_index

    @classmethod
    def color_preview(cls, name: str, width: int, height: int, color: Color) -> None:
        """ Create a widget with a preview of a color. """
        widget = cls.widget(name, width, height)
        data = cls.cached_data(name, width=0, height=0)

        if cls._textures_reset or width != data['width'] or height != data['height']:
            data['width'] = width
            data['height'] = height
            data['checkerboard'] = cls._transparent_checkerboard_texture(width, height)

        Renderer.copy(
            texture=data['checkerboard'],
            source_rect=None,
            destination_rect=widget['rect'],
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )
        widget['rect'].draw(cls._camera, color, solid=True)

    @classmethod
    def rgb_sliders(cls, name: str, width: int, color: Color) -> Color:
        """ Create a group of RGB sliders. """
        return cls._rgba_sliders(name, width, color, include_alpha=False)

    @classmethod
    def rgba_sliders(cls, name: str, width: int, color: Color) -> Color:
        """ Create a group of RGBA sliders. """
        return cls._rgba_sliders(name, width, color, include_alpha=True)

    @classmethod
    def hsv_sliders(cls, name: str, width: int, color: Color) -> Color:
        """ Create a group of HSV sliders. """
        return cls._hsva_sliders(name, width, color, include_alpha=False)

    @classmethod
    def hsva_sliders(cls, name: str, width: int, color: Color) -> Color:
        """ Create a group of HSVA sliders. """
        return cls._hsva_sliders(name, width, color, include_alpha=True)

    @classmethod
    def color_box(cls, name: str, width: int, height: int, color: Color) -> Color:
        """ Create a color box widget. """
        # Create widget
        widget = cls.widget(name, width, height)

        # Get cached data
        hue = color.hue()
        data = cls.cached_data(name, rgb=None, hue=hue)

        if data['rgb'] == color[:3]:
            hue_changed = False
            hue = data['hue']
        else:
            hue_changed = True
            data['hue'] = hue

        # Change the color if the widget was clicked
        if widget['held']:
            # Calculate geometry
            left = widget['rect'].left()
            right = widget['rect'].right()
            top = widget['rect'].top()
            bottom = widget['rect'].bottom()

            # Get mouse position
            mouse_x, mouse_y = cls.mouse()
            mouse_x = pmath.clamp(mouse_x, left, right)
            mouse_y = pmath.clamp(mouse_y, top, bottom)

            # Calculate saturation and value from mouse position
            saturation = int(pmath.remap(mouse_x, left, right, 0, 100))
            value = int(pmath.remap(mouse_y, top, bottom, 100, 0))

            # Set new color
            alpha = color.a
            color = Color.from_hsv(hue, saturation, value)
            color.a = alpha
            data['rgb'] = color[:3]

        # Get cached texture
        if hue_changed or cls._textures_reset:
            data['texture'] = cls._color_box_gradient(hue)

        # Draw the gradient texture
        Renderer.copy(
            texture=data['texture'],
            source_rect=None,
            destination_rect=widget['rect'],
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw the color picker
        x = widget['rect'].x + int(width * color.saturation() / 100)
        y = widget['rect'].y + int(height - (height * color.value() / 100))
        circle = Circle(x, y, COLOR_BOX_PICKER_RADIUS)

        if color.value() > 50:
            picker_color = Color.black()
        else:
            picker_color = Color.white()

        circle.draw(cls._camera, picker_color)

        return color

    @classmethod
    def hue_ribbon(cls, name: str, width: int, height: int, color: Color) -> Color:
        """ Create a hue ribbon widget. """
        # Create widget
        widget = cls.widget(name, width, height)
        data = cls.cached_data(name)

        # Change the color if the widget was clicked
        if widget['held']:
            left = widget['rect'].left()
            right = widget['rect'].right()

            mouse_x = pmath.clamp(cls.mouse().x, left, right)

            hue = int(pmath.remap(mouse_x, left, right, 0, 360))
            color = Color.from_hsv(hue, color.saturation(), color.value())

        # Get cached gradient texture
        if 'texture' not in data or cls._textures_reset:
            data['texture'] = cls._hue_slider_gradient()

        # Draw the gradient
        Renderer.copy(
            texture=data['texture'],
            source_rect=None,
            destination_rect=widget['rect'],
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw the color picker
        x = widget['rect'].x + int(width * color.hue() / 360)
        y = widget['rect'].center().y
        circle = Circle(x, y, COLOR_BOX_PICKER_RADIUS)
        circle.draw(cls._camera, Color.black())

        return color

    @classmethod
    def alpha_ribbon(cls, name: str, width: int, height: int, color: Color) -> Color:
        """ Create an alpha ribbon widget. """
        # Create widget
        widget = cls.widget(name, width, height)
        data = cls.cached_data(name, color=None, width=width, height=height)

        # Change the color if the widget was clicked
        if widget['held']:
            left = widget['rect'].left()
            right = widget['rect'].right()

            mouse_x = pmath.clamp(cls.mouse().x, left, right)

            alpha = int(pmath.remap(mouse_x, left, right, 0, 255))
            color = Color(color.r, color.g, color.b, alpha)

        # Get cached textures
        if data['color'] != color or cls._textures_reset or width != data['width'] or height != data['height']:
            data['color'] = color
            data['width'] = width
            data['height'] = height
            data['gradient'] = cls._channel_slider_gradient(
                width,
                height,
                Color(color.r, color.g, color.b, 0),
                Color(color.r, color.g, color.b)
            )

        # Draw the gradient
        Renderer.copy(
            texture=data['gradient'],
            source_rect=None,
            destination_rect=widget['rect'],
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Draw the color picker
        x = widget['rect'].x + int(width * color.a / 255)
        y = widget['rect'].center().y
        circle = Circle(x, y, COLOR_BOX_PICKER_RADIUS)

        if color.value() > 50:
            picker_color = Color.black()
        else:
            picker_color = Color.white()

        circle.draw(cls._camera, picker_color)

        return color

    @classmethod
    def combo_box(cls, name: str, current_index: int, options: list[str]) -> int:
        """ Create a combo box widget.
        Returns the index of the current item.
        """
        # Get text
        text_list = cls.cached_text_list(options, suffix=f"{name}__Option")

        # Calculate sizes
        max_text_width = max([t.width for t in text_list])
        max_text_height = max([t.height for t in text_list])
        width = max_text_width + COMBO_BOX_ARROW_WIDTH + BUTTON_X_PADDING * 3
        height = max_text_height + BUTTON_DEPTH + BUTTON_Y_PADDING * 2

        # Create widget
        widget = cls._button(name, width, height)
        button_rect, shadow_rect = cls._button_rects(widget)
        color = cls._button_color(widget)

        # Draw combo box
        Renderer.draw_rounded_rect_solid(shadow_rect, COMBO_BOX_RADIUS, cls.style("button_shadow"))
        Renderer.draw_rounded_rect_solid(button_rect, COMBO_BOX_RADIUS, color)

        # Draw arrow
        arrow_position = Point(
            button_rect.right() - BUTTON_X_PADDING - COMBO_BOX_ARROW_WIDTH,
            button_rect.center().y + 1 - COMBO_BOX_ARROW_HEIGHT // 2,
        )
        vertices = [
            arrow_position,
            arrow_position + Point(COMBO_BOX_ARROW_WIDTH // 2, COMBO_BOX_ARROW_HEIGHT),
            arrow_position + Point(COMBO_BOX_ARROW_WIDTH, 0),
        ]
        Renderer.render_geometry(vertices, cls.style("combo_box_text"))

        # Draw text
        text = text_list[current_index]
        text_x = button_rect.x + BUTTON_X_PADDING
        text_y = button_rect.y + (button_rect.height - text.height) // 2
        text.color = cls.style("combo_box_text")
        text.draw(cls._camera, Point(text_x, text_y))

        # Open menu if clicked
        menu_name = f"{name}__Menu"
        if widget['clicked']:
            cls.open_menu(menu_name, shadow_rect.bottom_left())

        # Show menu
        if cls.menu(menu_name):
            for i, option in enumerate(options):
                if current_index == i:
                    with cls.style_override(menu_item_text=cls.style("combo_box_text_current")):
                        if cls.menu_item(option):
                            current_index = i
                else:
                    if cls.menu_item(option):
                        current_index = i
            cls.end_menu()

        return current_index

    @classmethod
    def list_box(cls,
                 name: str,
                 width: int,
                 height: int,
                 current_index: int,
                 options: list[str],
                 alternate_row_colors: bool = False
                 ) -> int:
        """ Create a list widget.
        Returns the index of the current item.
        An index of -1 indicates that no item is selected.
        """
        # Create header
        header_text = cls.cached_text(name)
        header_text.color = cls.style("list_box_header_text")
        if header_text.text:
            # Calculate header height
            _, header_height = cls._button_size(header_text, None)

            # Create header widget
            header_widget = cls.widget(name, width, header_height)
            _, header_rect = cls._button_rects(header_widget)

            # Header color
            if cls.disabled():
                header_color = cls.style("list_box_header_disabled")
            else:
                header_color = cls.style("list_box_header")

            # Draw background
            Renderer.draw_rect_with_optional_rounded_corners_solid(
                header_rect,
                BUTTON_RADIUS,
                True,
                True,
                False,
                False,
                header_color
            )

            # Draw header text
            text_position = Point(
                header_widget['rect'].x + BUTTON_X_PADDING,
                header_widget['rect'].y + BUTTON_Y_PADDING,
            )
            header_text.draw(cls._camera, text_position)

            # Draw background
            background_rect = Rect(
                header_widget['rect'].x,
                header_widget['rect'].y + header_height,
                header_widget['rect'].width,
                height - header_height,
            )
            Renderer.draw_rect_with_optional_rounded_corners_solid(
                background_rect,
                BUTTON_RADIUS,
                False,
                False,
                True,
                True,
                cls.style("list_box_background")
            )
        else:
            # If there is no header, just draw a background
            background_rect = Rect(cls._cx, cls._cy, width, height)
            Renderer.draw_rounded_rect_solid(background_rect, BUTTON_RADIUS, cls.style("list_box_background"))

        # list_item_text_selected_background

        # Create scroll area for list items
        with cls.sub_region(background_rect):
            cls.set_cursor(
                cls._cx + LIST_BOX_CONTENT_PADDING,
                cls._cy + LIST_BOX_CONTENT_PADDING
            )
            scroll_area_width = background_rect.width - GROUP_BOX_CONTENT_PADDING * 2
            scroll_area_height = background_rect.height - GROUP_BOX_CONTENT_PADDING * 2
            with cls.scroll_area(f"{name}__ScrollArea", scroll_area_width, scroll_area_height):
                # Create all list items
                with cls.y_spacing(1):
                    for i, option in enumerate(options):
                        # Get cached text
                        list_item_name = f"{option}##__ListItem"
                        list_item_text = cls.cached_text(list_item_name)
                        if cls.disabled():
                            list_item_text.color = cls.style("text_disabled")
                        else:
                            list_item_text.color = cls.style("text")

                        # Create list item widget
                        list_item_height = list_item_text.height + LIST_BOX_CONTENT_PADDING * 2
                        list_item_widget = cls.widget(list_item_name, cls.available_x(), list_item_height)

                        # Change current index if clicked
                        if list_item_widget['clicked']:
                            current_index = i

                        # Draw alternate row background
                        if alternate_row_colors and i % 2 == 0:
                            list_item_widget['rect'].draw(cls._camera, cls.style("list_box_background_alternate"), True)

                        # Check if we're drawing a background
                        draw_background = False
                        if i == current_index:
                            draw_background = True
                            list_item_text.color = cls.style("list_box_item_text_selected")
                            if cls.disabled():
                                background_color = cls.style("list_box_item_text_selected_background_disabled")
                            else:
                                background_color = cls.style("list_box_item_text_selected_background")
                        elif list_item_widget['hovered'] and not cls.disabled():
                            draw_background = True
                            background_color = cls.style("list_box_item_text_hovered_background")
                            list_item_text.color = cls.style("list_box_item_text_selected")

                        # Draw background
                        if draw_background:
                            Renderer.draw_rounded_rect_solid(
                                list_item_widget['rect'],
                                LIST_BOX_ITEM_BACKGROUND_RADIUS,
                                background_color
                            )

                        # Draw text
                        list_item_text_x = list_item_widget['rect'].x + LIST_BOX_ITEM_X_PADDING
                        list_item_text_y = list_item_widget['rect'].y + LIST_BOX_ITEM_Y_PADDING
                        list_item_text_position = Point(list_item_text_x, list_item_text_y)
                        list_item_text.draw(cls._camera, list_item_text_position)

                    # Add an invisible widget to pad the rest of the empty space (if any)
                    # Clicking this widget will clear the selection
                    if cls.available_x() and cls.available_y():
                        invisible_background_widget = cls.widget(
                            f"{name}__InvisibleBackgroundWidget",
                            cls.available_x(),
                            cls.available_y()
                        )
                        if invisible_background_widget['pressed']:
                            current_index = -1

        cls._update_cursor_after_placement(background_rect)

        return current_index

    @classmethod
    def text_input(cls, name: str, width: int, height: int, text: str, wrap: bool = True) -> str:
        """ Create a text input widget. """
        return cls._input(name, width, height, text, wrap=wrap, multiline=True)

    @classmethod
    def line_input(cls, name: str, width: int, text: str, label: bool = False, reset: Any = None) -> str:
        """ Create a single-line text input widget. """
        height = cls.line_height() + INPUT_CONTENT_PADDING * 2
        regex = r'[^\n\t]*'
        return cls._input(name, width, height, text, label=label, reset=reset, regex=regex)

    @classmethod
    def int_input(cls, name: str, width: int, value: int, label: bool = False, reset: Any = None) -> int:
        """ Create an integer input widget. """
        height = cls.line_height() + INPUT_CONTENT_PADDING * 2
        regex = r'(\-)?[\d]*'
        new_value = cls._input(name, width, height, str(value), label=label, reset=reset, regex=regex)
        if not new_value or new_value == "-":
            return value
        return int(new_value)

    @classmethod
    def float_input(cls, name: str, width: int, value: float, label: bool = False, reset: Any = None) -> float:
        """ Create a floating point input widget. """
        height = cls.line_height() + INPUT_CONTENT_PADDING * 2
        regex = r'(\-)?\d+(\.\d+)?'
        new_value = cls._input(name, width, height, str(value), label=label, reset=reset, regex=regex)
        if not new_value or new_value == "-":
            return value
        return float(new_value)

    @classmethod
    def hex_color_input(cls, name: str, width: int, color: Color, label: bool = False, reset: Color = None) -> Color:
        """ Create a hex color input widget. """
        if reset:
            reset = reset.hex()

        height = cls.line_height() + INPUT_CONTENT_PADDING * 2
        regex = r'#?[0-9a-fA-F]{0,6}'
        new_value = cls._input(name, width, height, color.hex(), label=label, reset=reset, regex=regex)

        # Pad with zeroes if it's an incomplete hex code
        if new_value.startswith("#"):
            new_value = new_value.ljust(7, "0")
        else:
            new_value = new_value.ljust(6, "0")

        # Add original alpha back
        new_color = Color.from_hex(new_value)
        new_color.a = color.a

        return new_color

    @classmethod
    def group_inputs(cls, inputs: list[str]) -> None:
        """ Group inputs together for Tab navigation. """
        if Keyboard.get_key_down(Keyboard.TAB):
            current_widget = None
            new_widget = None

            # Get the current focused widget, and the new widget to focus
            for i, name in enumerate(inputs):
                if data := cls._data_cache.get(name):
                    if data.get('focused'):
                        # Set the current widget
                        current_widget = name

                        # Set the new widget
                        if Keyboard.get_shift():
                            # If Shift is being held, the new widget is the previous one.
                            new_widget = inputs[i-1]
                        elif i == len(inputs) - 1:
                            new_widget = inputs[0]
                        else:
                            new_widget = inputs[i+1]

            if not current_widget or not new_widget:
                return

            # Unfocus the current widget
            cls._data_cache[current_widget]['focused'] = False
            cls._data_cache[current_widget]['cursor'] = 0
            cls._data_cache[current_widget]['selection'] = None
            cls._data_cache[current_widget]['undo_queue'].clear()
            cls._data_cache[current_widget]['redo_queue'].clear()

            # Focus the new widget
            if data := cls._data_cache.get(new_widget):
                index = len(data['s'])
                data['focused'] = True
                data['focused_time'] = 0
                data['cursor'] = index
                data['selection'] = (0, index - 1)

    @classmethod
    @contextmanager
    def scroll_area(cls,
                    name: str,
                    width: int,
                    height: int,
                    force_horizontal: bool | None = None,
                    force_vertical: bool | None = None
                    ) -> Generator:
        """ Create a scroll area.
        `force_horizontal` and `force_vertical` determine the visibility of the scroll bars for each axis:
            If None (the default), the visibility is calculated based on whether or not the content fits the scroll area
            If True, the bar is always visible
            If False, the bar is never visible
        """
        # Create widget
        widget = cls.widget(name, width, height)
        cls.save_cursor()

        # Get cached data
        data = cls.cached_data(
            name,
            scroll_x=0,
            scroll_y=0,
            content_width=0,
            content_height=0,
        )

        # Calculate geometry
        content_rect, horizontal_bar_rect, vertical_bar_rect = cls._scroll_area_rects(
            widget['rect'],
            data['content_width'],
            data['content_height'],
            force_horizontal,
            force_vertical
        )

        # Get scroll amount in absolute pixel values
        scroll_x = data['scroll_x']
        scroll_y = data['scroll_y']

        # Get the maximum scroll values
        scroll_x_max = data['content_width'] - content_rect.width
        scroll_y_max = data['content_height'] - content_rect.height

        # Create horizontal scroll bar widget
        if horizontal_bar_rect:
            cls.set_cursor(horizontal_bar_rect.x, horizontal_bar_rect.y)
            scroll_x = cls._horizontal_scroll_bar(
                f"{name}__HorizontalScrollBar",
                horizontal_bar_rect.width,
                scroll_x,
                0,
                scroll_x_max
            )

        # Create vertical scroll bar widget
        if vertical_bar_rect:
            cls.set_cursor(vertical_bar_rect.x, vertical_bar_rect.y)
            scroll_y = cls._vertical_scroll_bar(
                f"{name}__VerticalScrollBar",
                vertical_bar_rect.height,
                scroll_y,
                0,
                scroll_y_max
            )

        # Mouse scroll
        if cls._mouse_scroll_wheel and not cls.disabled():
            if widget['rect'].contains_point(cls.mouse()):
                if Keyboard.get_shift():
                    scroll_x -= cls._mouse_scroll_wheel
                else:
                    scroll_y -= cls._mouse_scroll_wheel

        # Constrain the scroll amount so that it can't scroll past the boundaries
        scroll_x = pmath.clamp(scroll_x, 0, scroll_x_max)
        scroll_y = pmath.clamp(scroll_y, 0, scroll_y_max)

        # Store the new scroll amount
        data['scroll_x'] = scroll_x
        data['scroll_y'] = scroll_y

        # Create a sub-region for the scroll area content
        with cls.sub_region(content_rect):
            # Offset the cursor by the scroll amount
            scroll_offset_x = content_rect.x - scroll_x
            scroll_offset_y = content_rect.y - scroll_y
            cls.set_cursor(scroll_offset_x, scroll_offset_y)

            cls.start_bbox()
            yield
            cls.end_bbox()

        # Update the content size
        if cls.bbox():
            data['content_width'] = cls.bbox().width
            data['content_height'] = cls.bbox().height

        # Restore cursor
        cls.restore_cursor()

    @classmethod
    @contextmanager
    def group_box(cls, name: str, width: int, height: int, collapsible: bool = False) -> Generator:
        """ Create a group box. """
        # Text
        text = cls.cached_text(name)
        text.color = cls.style("group_box_header_text")

        # Calculate header height
        _, header_height = cls._button_size(text, None)

        # Create header widget
        widget = cls.widget(name, width, header_height)
        _, header_rect = cls._button_rects(widget)

        # Calculate the background rect
        background_rect = Rect(header_rect.x, header_rect.y, width, height - BUTTON_DEPTH)

        # Collapsed state
        data = cls.cached_data(name, collapsed=False)
        if collapsible and widget['clicked']:
            data['collapsed'] = not data['collapsed']

        collapsed = data['collapsed']

        # Header color
        if cls.disabled():
            header_color = cls.style("group_box_header_disabled")
        elif not collapsible:
            header_color = cls.style("group_box_header")
        elif widget['held'] or widget['dragged']:
            header_color = cls.style("group_box_header_pressed")
        elif widget['hovered']:
            header_color = cls.style("group_box_header_hovered")
        else:
            header_color = cls.style("group_box_header")

        # Draw header, outline, and background
        if collapsed:
            Renderer.draw_rounded_rect_solid(header_rect, BUTTON_RADIUS, header_color)
        else:
            Renderer.draw_rounded_rect_solid(background_rect, BUTTON_RADIUS, cls.style("group_box_background"))
            Renderer.draw_rounded_rect_outline(background_rect, BUTTON_RADIUS, header_color)
            Renderer.draw_rect_with_optional_rounded_corners_solid(
                header_rect,
                BUTTON_RADIUS,
                True,
                True,
                False,
                False,
                header_color
            )

        # Draw header text
        text_position = Point(
            widget['rect'].x + BUTTON_X_PADDING,
            widget['rect'].y + BUTTON_Y_PADDING,
        )
        text.draw(cls._camera, text_position)

        if collapsed:
            with cls._null_render_target():
                yield
        else:
            content_rect = Rect(
                widget['rect'].x,
                widget['rect'].y + header_height,
                widget['rect'].width,
                height - header_height,
            )
            with cls.sub_region(content_rect):
                cls.set_cursor(
                    cls._cx + GROUP_BOX_CONTENT_PADDING,
                    cls._cy + GROUP_BOX_CONTENT_PADDING
                )
                scroll_area_width = content_rect.width - GROUP_BOX_CONTENT_PADDING * 2
                scroll_area_height = content_rect.height - GROUP_BOX_CONTENT_PADDING * 2
                with cls.scroll_area(f"{name}__ScrollArea", scroll_area_width, scroll_area_height):
                    yield

            cls._update_cursor_after_placement(background_rect)

    @classmethod
    def open_window(cls,
                    name: str,
                    size: tuple[int, int],
                    *,
                    min_width: int = 0,
                    max_width: int = 0,
                    min_height: int = 0,
                    max_height: int = 0,
                    title_bar: bool = True,
                    can_close: bool = False,
                    can_resize: bool = False,
                    modal: bool = False,
                    position: Point | None = None,
                    ) -> None:
        """ Flag a window as open, and start a cache. """
        cls._open_windows.add(name)

        if not position:
            x = (cls._width - size[0]) // 2
            y = (cls._height - size[1]) // 2
        else:
            x = position.x
            y = position.y

        cls.cached_data(
            name,
            rect=Rect(x, y, size[0], size[1]),
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            title_bar=title_bar,
            can_close=can_close,
            can_resize=can_resize,
            modal=modal,
        )

        # If this is a modal dialog, set it as the new modal dialog and close any existing one
        if modal:
            if cls._modal and cls._modal != name:
                Log.warning(f"'{name}' has closed existing modal window '{cls._modal}'")
                cls.close_window(cls._modal)
            cls._modal = name

    @classmethod
    def close_window(cls, name: str) -> None:
        """ Close a window. """
        try:
            cls._open_windows.remove(name)
            if cls._data_cache[name]['modal']:
                cls._modal = None
        except KeyError:
            pass

    @classmethod
    def window(cls, name: str) -> bool:
        """ Create a window.
        If the window name has not been opened with `open_window()`, then this method will return False immediately.
        Otherwise, the window construction will start, and this method will return True.

        The position, width, and height are only used the first frame the window is shown. After that, they are pulled
            from the cache. This allows the window to move and be resized.
        """
        # Exit if the window hasn't been opened
        if name not in cls._open_windows:
            return False

        # Add window to stack
        cls._window_stack.append(name)

        # Get window data
        data = cls.cached_data(name)
        rect = data['rect']
        min_width = data['min_width']
        min_height = data['min_height']
        title_bar = data['title_bar']
        can_close = data['can_close']
        can_resize = data['can_resize']

        # Switch to the layer texture
        if data['modal']:
            cls._start_layer(LAYER_MODAL)
        else:
            cls._start_layer(LAYER_WINDOW)

        # Initialize x, y, width, and height
        # These can be manipulated by moving or resizing the window
        x = rect.x
        y = rect.y
        width = rect.width
        height = rect.height

        # Calculate content area
        content_x = x + WINDOW_CONTENT_PADDING
        content_y = y + WINDOW_CONTENT_PADDING
        content_width = width - WINDOW_CONTENT_PADDING * 2
        content_height = height - WINDOW_CONTENT_PADDING * 2
        if title_bar:
            content_y += WINDOW_TITLE_BAR_HEIGHT
            content_height -= WINDOW_TITLE_BAR_HEIGHT
        if can_resize:
            content_width -= math.isqrt(WINDOW_RESIZE_HANDLE_SIZE)
            content_height -= math.isqrt(WINDOW_RESIZE_HANDLE_SIZE)
        content_rect = Rect(content_x, content_y, content_width, content_height)

        # Get text from cache, or create new text
        title_text = cls.cached_text(name)
        title_text.color = cls.style("window_title_text")
        title_text.align_vertical_center()

        # Save cursor
        cls.save_cursor()

        # Create window widget
        cls.set_cursor(x, y)
        cls.widget(name, width, height)

        # Draw window background
        Renderer.draw_rounded_rect_solid(rect, WINDOW_RADIUS, cls.style("window_background"))
        Renderer.draw_rounded_rect_outline(rect, WINDOW_RADIUS, cls.style("window_outline"))

        # Create title bar widget
        if title_bar:
            if can_close:
                title_bar_width = width - WINDOW_TITLE_BAR_HEIGHT
                title_bar_corners = (True, False, False, False)
            else:
                title_bar_width = width
                title_bar_corners = (True, True, False, False)

            cls.set_cursor(x, y)
            title_bar_widget = cls.widget(f"{name}__TitleBar", title_bar_width, WINDOW_TITLE_BAR_HEIGHT)

            # Draw title bar background
            title_bar_rect = title_bar_widget['rect']
            Renderer.draw_rect_with_optional_rounded_corners_solid(
                title_bar_rect,
                WINDOW_RADIUS,
                title_bar_corners[0],
                title_bar_corners[1],
                title_bar_corners[2],
                title_bar_corners[3],
                cls.style("window_outline")
            )

            # Draw title text
            title_text_x = title_bar_rect.x + WINDOW_CONTENT_PADDING
            title_text_y = title_bar_rect.center().y
            title_text.draw(cls._camera, Point(title_text_x, title_text_y))

            # Create close button widget
            if can_close:
                cls.set_cursor(x + title_bar_width, y)
                close_button_widget = cls.widget(f"{name}__XButton", WINDOW_TITLE_BAR_HEIGHT, WINDOW_TITLE_BAR_HEIGHT)

                # Close button color
                if close_button_widget['held'] or close_button_widget['dragged']:
                    close_x_color = cls.style("window_outline")
                    close_button_color = cls.style("window_close_button_pressed")
                elif close_button_widget['hovered']:
                    close_x_color = cls.style("window_outline")
                    close_button_color = cls.style("window_close_button_hovered")
                else:
                    close_x_color = cls.style("window_title_text")
                    close_button_color = cls.style("window_outline")

                # Draw close button
                Renderer.draw_rect_with_optional_rounded_corners_solid(
                    close_button_widget['rect'],
                    WINDOW_RADIUS,
                    False,
                    True,
                    False,
                    False,
                    close_button_color
                )

                # Draw "X" lines
                close_button_offset = close_button_widget['rect'].position()

                l1 = Line(
                    WINDOW_CLOSE_BUTTON_X_P0 + close_button_offset,
                    WINDOW_CLOSE_BUTTON_X_P1 + close_button_offset
                )
                l2 = Line(
                    WINDOW_CLOSE_BUTTON_X_P2 + close_button_offset,
                    WINDOW_CLOSE_BUTTON_X_P3 + close_button_offset
                )

                l1.draw(cls._camera, close_x_color)
                l2.draw(cls._camera, close_x_color)

                # Close the window if the close button was clicked
                if close_button_widget['clicked']:
                    cls.close_window(name)

            # Move window if the title bar is dragged
            if title_bar_widget['dragged']:
                x, y = title_bar_widget['drag_start'] + cls._mouse_drag_delta

        # Create resize handle widget
        if can_resize:
            resize_handle_x = rect.right() - WINDOW_RESIZE_HANDLE_SIZE
            resize_handle_y = rect.bottom() - WINDOW_RESIZE_HANDLE_SIZE
            resize_handle_w = WINDOW_RESIZE_HANDLE_SIZE
            resize_handle_h = WINDOW_RESIZE_HANDLE_SIZE

            cls.set_cursor(resize_handle_x, resize_handle_y)
            resize_handle_widget = cls.widget(f"{name}__ResizeHandle", resize_handle_w, resize_handle_h)

            # Resize handle color
            if resize_handle_widget['hovered']:
                resize_handle_color = cls.style("window_resize_handle_hovered")
            else:
                resize_handle_color = cls.style("window_outline")

            # Draw resize handle
            resize_handle_vertices = [
                WINDOW_RESIZE_HANDLE_P0 + rect.bottom_right(),
                WINDOW_RESIZE_HANDLE_P1 + rect.bottom_right(),
                WINDOW_RESIZE_HANDLE_P2 + rect.bottom_right(),
                WINDOW_RESIZE_HANDLE_P0 + rect.bottom_right(),
                WINDOW_RESIZE_HANDLE_P2 + rect.bottom_right(),
                WINDOW_RESIZE_HANDLE_P3 + rect.bottom_right(),
            ]
            Renderer.render_geometry(resize_handle_vertices, resize_handle_color)

            # Resize the window if the resize handle is dragged
            if resize_handle_widget['dragged']:
                original_size = (
                        resize_handle_widget['drag_start'] -
                        rect.position() +
                        resize_handle_widget['rect'].size() +
                        Point.one()
                )
                width, height = original_size + cls._mouse_drag_delta

                # Prevent resizing past the edge of the window
                remainder_w = x + width - cls._width
                remainder_h = y + height - cls._height
                if remainder_w > 0:
                    width -= remainder_w
                if remainder_h > 0:
                    height -= remainder_h

            # Update mouse cursor
            if resize_handle_widget['hovered'] or resize_handle_widget['dragged']:
                cls.set_mouse_cursor(MOUSE_CURSOR_RESIZE_DIAGONAL_DOWN)

        # Enforce minimum size
        if not min_width:
            min_width = title_text.width + WINDOW_TITLE_BAR_HEIGHT + WINDOW_CONTENT_PADDING * 2
        if not min_height:
            min_height = WINDOW_TITLE_BAR_HEIGHT * 2
        if width < min_width:
            width = min_width
        if height < min_height:
            height = min_height

        # Constrain to screen
        if x + width > cls._width:
            x = cls._width - width
        if y + height > cls._height:
            y = cls._height - height
        if x < 0:
            x = 0
        if y < 0:
            y = 0

        # Update cached geometry
        data['rect'] = Rect(x, y, width, height)

        # Add a sub-region for the window content
        cls.start_sub_region(content_rect)
        cls.start_layout(LAYOUT_VERTICAL)

        return True

    @classmethod
    def end_window(cls) -> None:
        """ End the current window. """
        cls._window_stack.pop()
        cls.end_layout()
        cls.end_sub_region()
        cls.restore_cursor()

        # Render to the main GUI layer again
        cls._end_layer()

    @classmethod
    def open_menu(cls, name: str, position: Point) -> None:
        """ Open a menu. """
        cls.close_menus_at_depth()
        cls._open_menus.add(name)
        data = cls.cached_data(name)

        # Always reset the cached data so that the menu opens at the new position
        data['depth'] = cls._menu_depth
        data['position'] = position
        data['content_width'] = 0
        data['content_height'] = 0

    @classmethod
    def close_menu(cls, name: str) -> None:
        """ Close a menu. """
        try:
            cls._open_menus.remove(name)
        except KeyError:
            pass

    @classmethod
    def close_menus_at_depth(cls) -> None:
        """ Close all menus at (or greater than) the current depth. """
        close = []
        for menu in cls._open_menus:
            if data := cls.cached_data(menu):
                if data['depth'] >= cls._menu_depth:
                    close.append(menu)

        for m in close:
            cls.close_menu(m)

    @classmethod
    def close_all_menus(cls) -> None:
        """ Close all menus. """
        cls._open_menus.clear()

    @classmethod
    def menu(cls, name: str, min_width: int = 0) -> bool:
        """ Create a menu.
        Returns True if the menu is open.
        """
        # Exit if the menu is not open
        if name not in cls._open_menus:
            return False

        # If this is the first menu, render to the menu texture
        if cls._menu_depth == 0:
            cls._start_layer(LAYER_MENU)

        # Increase the menu depth
        cls._menu_depth += 1

        # Add the menu to the stack
        cls._menu_stack.append(name)

        # Get menu data
        data = cls.cached_data(name)
        position = data['position']
        content_width = data['content_width']
        content_height = data['content_height']

        # Initialize x, y, width, and height
        x, y = position
        width = content_width + MENU_CONTENT_PADDING * 2
        if width < min_width:
            width = min_width
        height = content_height + MENU_CONTENT_PADDING * 2
        rect = Rect(x, y, width, height)

        # Save cursor
        cls.save_cursor()

        # Create menu widget
        cls.set_cursor(x, y)
        with cls.no_bbox():
            widget = cls.widget(name, width, height)

        # Check if the mouse is over the menu rect
        if widget['rect'].contains_point(cls.mouse()):
            cls._mouse_is_over_menu = True

        # Draw menu background
        # This is only done if the content size has been calculated, which prevents an ugly popping visual on the first
        #   frame that the menu is visible.
        if content_width and content_height:
            Renderer.draw_rounded_rect_solid(rect, MENU_RADIUS, cls.style("menu_background"))
            Renderer.draw_rounded_rect_outline(rect, MENU_RADIUS, cls.style("menu_outline"))

        # Set cursor position
        cls.set_cursor(x + MENU_CONTENT_PADDING, y + MENU_CONTENT_PADDING)

        # Start bounding box to measure the size of the menu content
        cls.start_bbox()

        return True

    @classmethod
    def end_menu(cls) -> None:
        """ End the current menu. """
        # Remove the menu from the stack
        name = cls._menu_stack.pop()

        # Decrease the menu depth
        cls._menu_depth -= 1

        # End the bounding box
        cls.end_bbox()

        # Set the menu data
        if cls.bbox():
            data = cls.cached_data(name)
            data['content_width'] = cls.bbox().width
            data['content_height'] = cls.bbox().height

        # Restore the cursor
        cls.restore_cursor()

        # If this ends the menu stack, render to the main GUI layer again
        if cls._menu_depth == 0:
            cls._end_layer()

    @classmethod
    def menu_item(cls, name: str) -> bool:
        """ Create a clickable menu item.
        Returns True if clicked.
        """
        # Get text from cache, or create new text
        text = cls.cached_text(name)

        if cls.disabled():
            text.color = cls.style("menu_item_text_disabled")
        else:
            text.color = cls.style("menu_item_text")

        # Calculate size
        width = text.width + MENU_ITEM_X_PADDING * 2
        height = text.height + MENU_ITEM_Y_PADDING * 2

        # Expand the width of the widget to match the width of the menu
        if cls._menu_stack:
            current_menu = cls._menu_stack[-1]
            menu_data = cls.cached_data(current_menu)
            content_width = menu_data['content_width']
            if width < content_width:
                width = content_width

        # Create widget
        widget = cls.widget(name, width, height)

        # Hovered behavior
        if widget['hovered']:
            # Close menus at depth
            cls.close_menus_at_depth()

            # Draw background
            Renderer.draw_rounded_rect_solid(
                widget['rect'],
                MENU_ITEM_RADIUS,
                cls.style("menu_item_background_hovered")
            )

            # Change text color
            text.color = cls.style("menu_item_text_hovered")

        # Draw text
        x = widget['rect'].x + MENU_ITEM_X_PADDING
        y = widget['rect'].y + MENU_ITEM_Y_PADDING
        text.draw(cls._camera, Point(x, y))

        # Close menus if item was clicked
        if widget['clicked']:
            cls.close_all_menus()

        return widget['clicked']

    @classmethod
    def menu_bar(cls, name: str, menus: list[str]) -> None:
        """ Create a menu bar widget.
        Each item in the `menus` list will create a new menu bar item.
        """
        height = cls.line_height() + MENU_ITEM_Y_PADDING

        # Background
        background_rect = Rect(cls._cx, cls._cy, cls.available_x(), height)
        background_rect.draw(cls._camera, cls.style("menu_bar"), solid=True)

        # Menu buttons
        with cls.horizontal_layout():
            for menu in menus:
                # Register text name
                text_name = f"{menu}##{name}__MenuBarItem"
                cls._register_name(text_name)

                # Get cached text
                text = cls.cached_text(text_name)
                text.align_vertical_center()
                text.color = cls.style("menu_item_text")

                # Calculate size
                width = text.width + MENU_ITEM_X_PADDING * 2

                # Create widget
                widget = cls.widget(f"{name}__{menu}", width, height)

                # Track whether the menu should be open
                open_menu = False

                # Hovered behavior
                if widget['hovered']:
                    # Draw background
                    Renderer.draw_rounded_rect_solid(
                        widget['rect'],
                        MENU_RADIUS,
                        cls.style("menu_item_background_hovered")
                    )

                    # Update text color
                    text.color = cls.style("menu_item_text_hovered")

                    # Open menu if another menu in this bar is already opened.
                    # This allows the behavior where you can open a menu with a single click, then hover the mouse over
                    #   other menu bar items to open their menus.
                    if cls._open_menus & set(menus):
                        open_menu = True

                # Clicked behavior
                if widget['clicked']:
                    open_menu = True

                # Open menu
                if open_menu:
                    if menu not in cls._open_menus:
                        menu_position = Point(
                            widget['rect'].x,
                            widget['rect'].y + height
                        )
                        cls.open_menu(menu, menu_position)

                # Draw text
                text_position = Point(
                    widget['rect'].x + MENU_ITEM_X_PADDING,
                    widget['rect'].center().y
                )
                text.draw(cls._camera, text_position)

        # Move cursor directly below the menu bar
        cls.set_cursor(background_rect.x, background_rect.bottom() + 1)

    @classmethod
    def menu_separator(cls) -> None:
        """ Create a horizontal line in a menu. """
        # Calculate rect and line
        if cls._menu_stack:
            current_menu = cls._menu_stack[-1]
            menu_data = cls.cached_data(current_menu)
            width = menu_data['content_width']
            rect = Rect(cls._cx, cls._cy, width, 1)
        else:
            # If the separator is created outside of a menu (which shouldn't really be done), just make a 2px line
            rect = Rect(cls._cx, cls._cy, 2, 1)

        line = Line(Point(rect.x, rect.center().y), Point(rect.right(), rect.center().y))

        # Draw line
        line.draw(cls._camera, cls.style("menu_separator"))

        cls._update_cursor_after_placement(rect)

    @classmethod
    def sub_menu(cls, name: str) -> bool:
        """ Create a sub-menu that starts a new menu when hovered.
        Returns True if the menu is open.
        """
        # Get text from cache, or create new text
        text = cls.cached_text(name)

        if cls.disabled():
            color = cls.style("menu_item_text_disabled")
        else:
            color = cls.style("menu_item_text")

        # Calculate size
        width = text.width + SUB_MENU_ARROW_SPACING + SUB_MENU_ARROW_WIDTH + MENU_ITEM_X_PADDING * 2
        height = text.height + MENU_ITEM_Y_PADDING * 2

        # Expand the width of the widget to match the width of the menu
        if cls._menu_stack:
            current_menu = cls._menu_stack[-1]
            menu_data = cls.cached_data(current_menu)
            content_width = menu_data['content_width']
            if width < content_width:
                width = content_width

        # Create widget
        widget = cls.widget(name, width, height)
        menu_name = f"{name}__Menu"

        # Hovered behavior
        if widget['hovered']:
            # Open menu
            if menu_name not in cls._open_menus:
                menu_position = widget['rect'].top_right()
                cls.open_menu(menu_name, menu_position)

            # Draw background
            Renderer.draw_rounded_rect_solid(
                widget['rect'],
                MENU_ITEM_RADIUS,
                cls.style("menu_item_background_hovered")
            )

            # Update color
            color = cls.style("menu_item_text_hovered")

        # Draw text
        text_x = widget['rect'].x + MENU_ITEM_X_PADDING
        text_y = widget['rect'].y + MENU_ITEM_Y_PADDING
        text.color = color
        text.draw(cls._camera, Point(text_x, text_y))

        # Draw arrow
        arrow_position = Point(
            widget['rect'].right() - MENU_ITEM_X_PADDING - SUB_MENU_ARROW_WIDTH,
            widget['rect'].center().y + 1 - SUB_MENU_ARROW_HEIGHT // 2,
        )
        vertices = [
            arrow_position,
            arrow_position + Point(SUB_MENU_ARROW_WIDTH,  SUB_MENU_ARROW_HEIGHT // 2),
            arrow_position + Point(0, SUB_MENU_ARROW_HEIGHT),
        ]
        Renderer.render_geometry(vertices, color)

        # Create the menu
        return cls.menu(menu_name)

    @classmethod
    def cached_text(cls, name: str) -> Text:
        """ Get text from the cache.
        If one doesn't exist, it will be created.
        """
        text = cls._text_cache.get(name)

        if not text:
            text = Text(cls._font)
            text.tags_enabled = False
            text.text = name.split("##")[0]
            cls._text_cache[name] = text

        return text

    @classmethod
    def cached_text_list(cls, names: list[str], suffix: str) -> list[Text]:
        """ Get a list of text from the cache.
        This will also register the names of each text item retrieved.
        """
        text_list = []
        for name in names:
            name = f"{name}##{suffix}"
            cls._register_name(name)
            text_list.append(cls.cached_text(name))

        return text_list

    @classmethod
    def cached_data(cls, name: str, **kwargs) -> dict:
        """ Get data from the cache.
        If the data doesn't exist, it will be created as a dictionary from the keyword arguments provided.
        """
        data = cls._data_cache.get(name)

        if not data:
            data = kwargs
            cls._data_cache[name] = data

        return data

    @classmethod
    def _reset_textures(cls) -> None:
        """ Reset the GUI's render target textures. """
        cls._textures_reset = True

        window_w, window_h = Window.size()
        cls._width = window_w // cls._zoom
        cls._height = window_h // cls._zoom
        cls._destination_rect = Rect(0, 0, cls._width * cls._zoom, cls._height * cls._zoom)

        cls._texture = Texture.create_target(cls._width, cls._height)
        cls._texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)

        cls._window_texture = Texture.create_target(cls._width, cls._height)
        cls._window_texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)

        cls._menu_texture = Texture.create_target(cls._width, cls._height)
        cls._menu_texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)

        cls._modal_texture = Texture.create_target(cls._width, cls._height)
        cls._modal_texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)

        cls._null_texture = Texture.create_target(2, 2)

    @classmethod
    @contextmanager
    def _null_render_target(cls) -> Generator:
        """ Render to a null render target. """
        old_disabled = cls._disabled
        cls._disabled = True

        with Renderer.render_target(cls._null_texture):
            yield

        cls._disabled = old_disabled

    @classmethod
    def _set_region_clip_rect(cls) -> None:
        """ Set the clip rect to match the current region.
        If multiple sub-regions are nested, the clip rect will be the intersection of all sub-regions.
        """
        # Clear the clip rect if there are no sub-regions
        if not cls._layer_sub_region_stack():
            Renderer.set_clip_rect(None)
            return

        # Initialize the clip rect as the first sub-region
        clip_rect = cls._layer_sub_region_stack()[0]

        # Intersect the clip rect with each subsequent sub-region
        for rect in list(cls._layer_sub_region_stack())[1:]:
            clip_rect = Rect.intersection(clip_rect, rect)

        # Set the clip rect
        Renderer.set_clip_rect(clip_rect)

    @classmethod
    def _start_layer(cls, layer: int) -> None:
        """ Start rendering to a new layer texture. """
        cls._layer_stack.append(layer)
        Renderer.set_render_target(cls._layer_texture(layer))

    @classmethod
    def _end_layer(cls) -> None:
        """ Stop rendering to the layer texture and return to the previous layer. """
        cls._layer_stack.pop()
        Renderer.set_render_target(cls._layer_texture(cls._layer()))

    @classmethod
    def _layer(cls) -> int:
        """ Get the current layer. """
        if cls._layer_stack:
            return cls._layer_stack[-1]
        else:
            return LAYER_NONE

    @classmethod
    def _layer_texture(cls, layer: int) -> Texture:
        """ Get the texture for a layer. """
        if layer == LAYER_NONE:
            return cls._texture
        elif layer == LAYER_WINDOW:
            return cls._window_texture
        elif layer == LAYER_MENU:
            return cls._menu_texture
        elif layer == LAYER_MODAL:
            return cls._modal_texture

    @classmethod
    def _layer_sub_region_stack(cls) -> deque[Rect]:
        """ Get the sub-region stack for the current layer. """
        return cls._sub_region_stack[cls._layer()]

    @classmethod
    def _register_name(cls, name: str) -> None:
        """ Register a name.
        This indicates that a GUI item has been created this frame.
        """
        if __debug__:
            if name in cls._names:
                Log.error(f"{name} is already registered")

        cls._names.add(name)

    @classmethod
    def _channel_slider_gradient(cls, width: int, height: int, a: Color, b: Color) -> Texture:
        """ Create a gradient texture for a channel slider. """
        # Create base texture
        texture = Texture.create_target(width, height)

        # Add checkerboard to base if any transparency exists
        if a.a < 255 or b.a < 255:
            checkerboard = cls._transparent_checkerboard_texture(width, height, offset=2)
            with Renderer.render_target(texture):
                Renderer.copy(
                    texture=checkerboard,
                    source_rect=None,
                    destination_rect=None,
                    rotation_angle=0,
                    rotation_center=None,
                    flip=0
                )

        # Create gradient texture
        gradient_resolution = 8
        gradient_texture = Texture.create_target(gradient_resolution, 1)
        gradient_texture.set_blend_mode(BlendMode.BLEND)
        gradient_texture.set_scale_mode(ScaleMode.LINEAR)
        with Renderer.render_target(gradient_texture):
            for x in range(gradient_resolution):
                color = Color.lerp(a, b, x / (gradient_resolution - 1))
                Renderer.draw_point(Point(x, 0), color)

        # Copy gradient to base texture
        with Renderer.render_target(texture):
            Renderer.copy(
                texture=gradient_texture,
                source_rect=None,
                destination_rect=None,
                rotation_angle=0,
                rotation_center=None,
                flip=0
            )

        return texture

    @classmethod
    def _hue_slider_gradient(cls) -> Texture:
        """ Create a gradient texture for a hue slider. """
        hue_samples = 16  # The number of times the hue is sampled to create the gradient
        resolution = 8  # Higher resolution creates more accurate color blending between each sample
        texture = Texture.create_target((hue_samples - 1) * resolution, 1)
        texture.set_blend_mode(BlendMode.BLEND)
        texture.set_scale_mode(ScaleMode.LINEAR)

        hue_colors = []
        for i in range(hue_samples):
            h = int(360 * (i / (hue_samples - 1)))
            hue_colors.append(Color.from_hsv(h, 100, 100))

        with Renderer.render_target(texture):
            x = 0
            for i in range(hue_samples - 1):
                a = hue_colors[i]
                b = hue_colors[i+1]
                for r in range(resolution):
                    t = r / (resolution - 1)
                    color = Color.lerp(a, b, t)
                    Renderer.draw_point(Point(x, 0), color)
                    x += 1

        return texture

    @classmethod
    def _color_box_gradient(cls, hue: int, resolution: int = 16) -> Texture:
        """ Create a box gradient for a color box.
        The saturation increases along the x-axis, and the value decreases along the y-axis.
        """
        texture = Texture.create_target(resolution, resolution)
        texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)
        texture.set_scale_mode(ScaleMode.LINEAR)

        with Renderer.render_target(texture):
            for y in range(resolution):
                for x in range(resolution):
                    saturation = int(100 * (x / (resolution - 1)))
                    value = 100 - int(100 * (y / (resolution - 1)))
                    Renderer.draw_point(Point(x, y), Color.from_hsv(hue, saturation, value))

        return texture

    @classmethod
    def _transparent_checkerboard_texture(cls, width: int, height: int, size: int = 4, offset: int = 0) -> Texture:
        """ Create a checkerboard texture for drawing behind transparent images.
        `size` is the size of each checker square.
        `offset` is the y-offset at which the checkers are drawn.
        (Very short textures use the offset so the pattern looks like a checkerboard, rather than alternating squares.)
        """
        texture = Texture.create_target(width, height)
        texture.set_scale_mode(ScaleMode.LINEAR)

        with Renderer.render_target(texture):
            for y in range(height):
                for x in range(width):
                    if (x // size) % 2 == 0:
                        if ((y + offset) // size) % 2 == 0:
                            color = Color.white()
                        else:
                            color = Color(215, 215, 215)
                    else:
                        if ((y + offset) // size) % 2 == 0:
                            color = Color(215, 215, 215)
                        else:
                            color = Color.white()
                    Renderer.draw_point(Point(x, y), color)

        return texture

    @classmethod
    def _button(cls, name: str, width: int, height: int) -> Widget:
        """ Create a basic button. """
        return cls.widget(name, width, height + BUTTON_DEPTH)

    @classmethod
    def _button_size(cls, text: Text | None, sprite: Sprite | None) -> tuple[int, int]:
        """ Return the width and height of a button with the given contents. """
        width = 0
        height = 0

        if text:
            width += text.width
            height = text.height

        if sprite:
            width += sprite.width()
            height = sprite.height()

        if text and sprite:
            width += BUTTON_X_PADDING
            height = max(text.height, sprite.height())

        width += BUTTON_X_PADDING * 2
        height += BUTTON_Y_PADDING * 2

        return width, height

    @classmethod
    def _button_rects(cls, button: Widget) -> tuple[Rect, Rect]:
        """ Get the button and shadow rect (respectively) from a button widget. """
        rect = button['rect']
        button_rect = Rect(rect.x, rect.y, rect.width, rect.height - BUTTON_DEPTH)
        shadow_rect = Rect(rect.x, rect.y + BUTTON_DEPTH, rect.width, rect.height - BUTTON_DEPTH)

        if button['held'] or button['dragged']:
            return shadow_rect, shadow_rect

        return button_rect, shadow_rect

    @classmethod
    def _button_color(cls, button: Widget) -> Color:
        """ Get the color of a button, based on its state. """
        if cls.disabled():
            return cls.style("button_disabled")
        elif button['held'] or button['dragged']:
            return cls.style("button_pressed")
        elif button['hovered']:
            return cls.style("button_hovered")
        else:
            return cls.style("button")

    @classmethod
    def _button_content_positions(cls, button: Widget, text: Text | None, sprite: Sprite | None) -> tuple[Point, Point]:
        """ Get the text and sprite draw positions for a button.
        Returns a tuple of (text_position, sprite_position)
        """
        button_rect, _ = cls._button_rects(button)
        center_x, center_y = button_rect.center()

        # Text only
        if not sprite:
            text_x = center_x - text.width // 2
            text_y = center_y - text.height // 2
            return Point(text_x, text_y), Point.zero()

        # Sprite only
        if not text:
            sprite_x = center_x - sprite.width() // 2
            sprite_y = center_y - sprite.height() // 2
            return Point.zero(), Point(sprite_x, sprite_y)

        # Text and sprite
        sprite_x = button_rect.x + BUTTON_X_PADDING
        sprite_y = center_y - sprite.height() // 2

        text_x = sprite_x + sprite.width() + BUTTON_X_PADDING
        text_y = center_y - text.height // 2

        return Point(text_x, text_y), Point(sprite_x, sprite_y)

    @classmethod
    def _slider(cls, name: str, width: int) -> Widget:
        """ Create a basic slider. """
        return cls.widget(name, width, SLIDER_HANDLE_HEIGHT)

    @classmethod
    def _slider_handle_rect(cls, slider: Widget, percent: float) -> Rect:
        """ Get the handle rect for a slider widget. """
        x = slider['rect'].x + int((slider['rect'].width - SLIDER_HANDLE_WIDTH) * percent)
        y = slider['rect'].y
        return Rect(x, y, SLIDER_HANDLE_WIDTH, SLIDER_HANDLE_HEIGHT)

    @classmethod
    def _slider_track_rects(cls, slider: Widget, percent: float) -> tuple[Rect, Rect]:
        """ Get the track rects for a slider widget.
        Returns a tuple of (track_rect, fill_rect)
        """
        x = slider['rect'].x
        y = slider['rect'].y + (SLIDER_HANDLE_HEIGHT - SLIDER_TRACK_HEIGHT) // 2
        w = slider['rect'].width
        fill_w = int(w * percent)
        track_rect = Rect(x, y, w, SLIDER_TRACK_HEIGHT)
        track_fill_rect = Rect(x, y, fill_w, SLIDER_TRACK_HEIGHT)

        return track_rect, track_fill_rect

    @classmethod
    def _slider_drag_value(cls, slider: Widget, minimum: float, maximum: float) -> float:
        """ Get the slider value when the mouse is dragging it. """
        min_x = slider['rect'].x
        max_x = slider['rect'].right()
        new_x = cls.mouse().x
        new_percent = pmath.remap(new_x, min_x, max_x, 0, 1)
        return pmath.clamp(pmath.remap(new_percent, 0, 1, minimum, maximum), minimum, maximum)

    @classmethod
    def _rgba_sliders(cls, name: str, width: int, color: Color, include_alpha: bool) -> Color:
        """ Create a group of RGBA sliders. """
        input_names = []
        with cls.vertical_layout():
            with cls.horizontal_layout():
                r = cls._channel_slider(f"{name}__r", width, color.r, color, "r")
                r = cls.int_input(f"{name}__rInput", 30, r)
                input_names.append(f"{name}__rInput")
            with cls.horizontal_layout():
                g = cls._channel_slider(f"{name}__g", width, color.g, color, "g")
                g = cls.int_input(f"{name}__gInput", 30, g)
                input_names.append(f"{name}__gInput")
            with cls.horizontal_layout():
                b = cls._channel_slider(f"{name}__b", width, color.b, color, "b")
                b = cls.int_input(f"{name}__bInput", 30, b)
                input_names.append(f"{name}__bInput")
            if include_alpha:
                with cls.horizontal_layout():
                    a = cls._channel_slider(f"{name}__a", width, color.a, color, "a")
                    a = cls.int_input(f"{name}__aInput", 30, a)
                    input_names.append(f"{name}__aInput")
            else:
                a = color.a

        cls.group_inputs(input_names)
        return Color(r, g, b, a)

    @classmethod
    def _hsva_sliders(cls, name: str, width: int, color: Color, include_alpha: bool) -> Color:
        """ Create a group of HSV sliders.

        This is more complicated than the RGB sliders because data loss occurs when converting back and forth between
            color coordinate systems. For example, an HSV color with a Value of 0 could be any Hue or Saturation, so
            those are always calculated as 0.

        Therefore, every time this widget changes the color, we store the new color result, as well as the HSV channels.
            Then, reuse those cached values if the color hasn't changed.
        """
        # Convert the incoming color to HSV
        h, s, v = color.hsv()

        # Get cached data
        cls._register_name(name)
        data = cls.cached_data(name, rgb=color[:3], h=h, s=s, v=v)

        # If the incoming color has not changed since this widget last set it, use the stored HSV values instead
        if data['rgb'] == color[:3]:
            h = data['h']
            s = data['s']
            v = data['v']

        # Create sliders
        input_names = []
        with cls.vertical_layout():
            with cls.horizontal_layout():
                new_h = cls._channel_slider(f"{name}__h", width, h, color, "h")
                new_h = cls.int_input(f"{name}__hInput", 30, new_h)
                input_names.append(f"{name}__hInput")
            with cls.horizontal_layout():
                new_s = cls._channel_slider(f"{name}__s", width, s, color, "s")
                new_s = cls.int_input(f"{name}__sInput", 30, new_s)
                input_names.append(f"{name}__sInput")
            with cls.horizontal_layout():
                new_v = cls._channel_slider(f"{name}__v", width, v, color, "v")
                new_v = cls.int_input(f"{name}__vInput", 30, new_v)
                input_names.append(f"{name}__vInput")
            if include_alpha:
                with cls.horizontal_layout():
                    a = cls._channel_slider(f"{name}__a", width, color.a, color, "a")
                    a = cls.int_input(f"{name}__aInput", 30, a)
                    input_names.append(f"{name}__aInput")
            else:
                a = color.a

        cls.group_inputs(input_names)

        # Only return a new color if the new HSV values are different from the incoming HSV values
        if (h, s, v) != (new_h, new_s, new_v):
            # Only let one channel change
            if v != new_v:
                new_h = h
                new_s = s
            elif s != new_s:
                new_h = h
                new_v = v
            else:
                new_s = s
                new_v = v

            # Store the new color and HSV channel values
            color = Color.from_hsv(new_h, new_s, new_v)
            data['rgb'] = color[:3]
            data['h'] = new_h
            data['s'] = new_s
            data['v'] = new_v

        color.a = a
        return color

    @classmethod
    def _channel_slider(cls, name: str, width: int, value: int, color: Color, channel: str) -> int:
        """ Create a slider for a color channel.
        Returns the new channel value.
        """
        # Make sure channel is valid
        if __debug__:
            if channel not in "rgbahsv":
                Log.error(f"Channel slider does not support '{channel}' channel")
                return value

        # Update the cached data
        data = cls.cached_data(name, color=None, width=width)
        if data['color'] != color or cls._textures_reset or width != data['width']:
            data['color'] = color
            data['width'] = width
            data['texture'] = cls._channel_slider_texture(width, SLIDER_TRACK_HEIGHT, color, channel)

        # Create widget
        with cls.horizontal_layout():
            cls.text(f"{channel.upper()}##__{name}Label")
            widget = cls._slider(name, width)

        # Widget color
        if cls.disabled():
            handle_color = cls.style("channel_slider_handle_disabled")
        elif widget['held'] or widget['dragged']:
            handle_color = cls.style("channel_slider_handle_pressed")
        elif widget['hovered']:
            handle_color = cls.style("channel_slider_handle_hovered")
        else:
            handle_color = cls.style("channel_slider_handle")

        # Get max values for channel
        if channel == "h":
            max_value = 360
        elif channel in "sv":
            max_value = 100
        else:
            max_value = 255

        # Calculate geometry
        percent = pmath.remap(value, 0, max_value, 0.0, 1.0)
        handle_rect = cls._slider_handle_rect(widget, percent)
        track_rect, _ = cls._slider_track_rects(widget, percent)

        # Draw track
        if cls.disabled():
            track_rect.draw(cls._camera, cls.style("slider_track"), solid=True)
        else:
            Renderer.copy(
                texture=data['texture'],
                source_rect=None,
                destination_rect=track_rect,
                rotation_angle=0,
                rotation_center=None,
                flip=0
            )

        # Draw handle
        Renderer.draw_rounded_rect_solid(handle_rect, SLIDER_HANDLE_RADIUS, handle_color)

        # Drag
        if widget['held']:
            value = int(cls._slider_drag_value(widget, 0, max_value))

        return value

    @classmethod
    def _channel_slider_texture(cls, width: int, height: int, color: Color, channel: str) -> Texture:
        """ Create a texture for a channel slider. """
        match channel:
            case "r":
                return cls._channel_slider_gradient(
                    width,
                    height,
                    Color(0, color.g, color.b),
                    Color(255, color.g, color.b),
                )
            case "g":
                return cls._channel_slider_gradient(
                    width,
                    height,
                    Color(color.r, 0, color.b),
                    Color(color.r, 255, color.b),
                )
            case "b":
                return cls._channel_slider_gradient(
                    width,
                    height,
                    Color(color.r, color.g, 0),
                    Color(color.r, color.g, 255),
                )
            case "a":
                return cls._channel_slider_gradient(
                    width,
                    height,
                    Color(color.r, color.g, color.b, 0),
                    Color(color.r, color.g, color.b, 255),
                )
            case "h":
                return cls._hue_slider_gradient()
            case "s":
                return cls._channel_slider_gradient(
                    width,
                    height,
                    Color.from_hsv(color.hue(), 0, color.value()),
                    Color.from_hsv(color.hue(), 100, color.value()),
                )
            case "v":
                return cls._channel_slider_gradient(
                    width,
                    height,
                    Color.from_hsv(color.hue(), color.saturation(), 0),
                    Color.from_hsv(color.hue(), color.saturation(), 100),
                )

    @classmethod
    def _input(cls,
               name: str,
               width: int,
               height: int,
               s: str,
               *,
               label: bool = False,
               reset: Any = None,
               wrap: bool = False,
               multiline: bool = False,
               regex: str = "",
               ) -> str:
        """ Create an input field. """
        # Get cached data
        data = cls.cached_data(
            name,
            s=s,
            focused=False,
            focused_time=0,
            cursor=0,
            selection=None,
            scroll_x=0,
            scroll_y=0,
            undo_queue=deque(),
            redo_queue=deque(),
        )

        focused = data['focused']
        focused_time = data['focused_time']
        cursor = data['cursor']
        selection = data['selection']
        scroll_x = data['scroll_x']
        scroll_y = data['scroll_y']
        undo_queue = data['undo_queue']
        redo_queue = data['redo_queue']

        text = data.get('text')
        if not text:
            text = Text(cls._font)
            text.text = s
            text.tags_enabled = False
            text.effects_enabled = False
            data['text'] = text

        if label:
            label_text = data.get('label_text')
            if not label_text:
                label_text = Text(cls._font)
                label_text.text = name.split("##")[0]
                label_text.tags_enabled = False
                label_text.effects_enabled = False
                data['label_text'] = label_text
        else:
            label_text = None

        # Create widget
        background_rect = Rect(cls._cx, cls._cy, width, height)
        if label:
            with cls.horizontal_layout():
                with cls.x_spacing(2):
                    label_width = label_text.width + INPUT_LABEL_X_PADDING * 2
                    label_widget = cls.widget(f"{name}__Label", label_width, height)
                    widget = cls.widget(name, width - label_width, height)
                    cls._update_cursor_after_placement(widget['rect'])
        else:
            widget = cls.widget(name, width, height)

        # Calculate geometry
        content_rect = Rect(
            widget['rect'].x + INPUT_CONTENT_PADDING,
            widget['rect'].y + INPUT_CONTENT_PADDING,
            widget['rect'].width - INPUT_CONTENT_PADDING * 2,
            widget['rect'].height - INPUT_CONTENT_PADDING * 2,
        )

        if multiline:
            content_rect, horizontal_scroll_bar_rect, vertical_scroll_bar_rect = cls._scroll_area_rects(
                scroll_area_rect=content_rect,
                content_width=text.width,
                content_height=text.height,
                force_horizontal=None,
                force_vertical=None,
            )
        else:
            horizontal_scroll_bar_rect = None
            vertical_scroll_bar_rect = None

        # Reset value
        if reset is not None and label_widget['clicked']:
            s = str(reset)
            data['s'] = s

        # Set mouse cursor
        if widget['dragged'] or widget['hovered']:
            cls.set_mouse_cursor(MOUSE_CURSOR_TEXT_SELECT)

        # Set focused state
        if cls._left_mouse_pressed:
            if widget['hovered']:
                if not focused:
                    focused = True
                    focused_time = 0
            else:
                focused = False
                cursor = 0
                selection = None
                undo_queue.clear()
                redo_queue.clear()

        if not multiline and cls._input_return():
            focused = False
            cursor = 0
            selection = None
            undo_queue.clear()
            redo_queue.clear()

        # Update focused time
        if focused:
            focused_time += Time.delta_time_ms

        # Reset the scroll if focus was lost
        if not focused and not multiline:
            scroll_x = 0
            scroll_y = 0

        # Colors
        if cls.disabled():
            text_color = cls.style("text_disabled")
        elif focused:
            text_color = cls.style("text")
        else:
            text_color = cls.style("text")

        # If the value is being edited, use the cached value
        # This prevents values from instantly changing when doing type casting
        # For instance, a float of 3.140 would change to 3.14, preventing any trailing zeroes from being added
        if focused:
            s = data['s']

        # Update text
        text.text = s
        text.color = text_color
        if wrap:
            text.word_wrap = True
            text.max_line_width = content_rect.width - SCROLL_AREA_CONTENT_PADDING * 2

        # Draw background
        Renderer.draw_rounded_rect_solid(background_rect, INPUT_RADIUS, cls.style("input_background"))

        # Draw label
        if label:
            # Label color
            if cls.disabled():
                label_text_color = cls.style("input_button_text_disabled")
                label_button_color = cls.style("input_button_disabled")
            elif (label_widget['held'] or label_widget['dragged']) and reset is not None:
                label_text_color = cls.style("input_button_text_hovered")
                label_button_color = cls.style("input_button_pressed")
            elif label_widget['hovered'] and reset is not None:
                label_text_color = cls.style("input_button_text_hovered")
                label_button_color = cls.style("input_button_hovered")
            else:
                label_text_color = cls.style("input_button_text")
                label_button_color = cls.style("input_button")

            # Label text
            label_text.text = name.split("##")[0]
            label_text.color = label_text_color

            # Label rects
            Renderer.draw_rect_with_optional_rounded_corners_solid(
                label_widget['rect'],
                INPUT_RADIUS,
                True,
                False,
                True,
                False,
                label_button_color
            )
            label_text_position = Point(
                label_widget['rect'].x + INPUT_LABEL_X_PADDING,
                label_widget['rect'].y + INPUT_CONTENT_PADDING,
            )
            label_text.draw(cls._camera, label_text_position)

        # Draw outline
        if focused:
            Renderer.draw_rounded_rect_outline(background_rect, INPUT_RADIUS, cls.style("input_outline"))

        # Handle input
        if focused:
            # Store the old values
            old_cursor = cursor
            old_s = s
            old_selection = selection

            # Cursor movement
            new_cursor = cls._get_input_cursor_keyboard_movement(text, cursor, selection)
            mouse_position = cls.mouse() - content_rect.position() + Point(scroll_x, scroll_y)
            new_cursor = cls._get_input_cursor_mouse_movement(text, new_cursor, mouse_position)
            if old_cursor != new_cursor:
                focused_time = 0
                cursor = new_cursor

            selection = cls._update_input_selection(text, old_cursor, new_cursor, selection)

            # Split the text before and after the cursor
            if selection:
                s_pre = s[:selection[0]]
                s_post = s[selection[1] + 1:]
                s_selection = s[selection[0]:selection[1] + 1]
            else:
                s_pre = s[:cursor]
                s_post = s[cursor:]
                s_selection = ""

            # Copy
            if cls._input_copy():
                Clipboard.set_text(s_selection)

            # Cut
            if cls._input_cut():
                focused_time = 0
                Clipboard.set_text(s_selection)
                cursor = len(s_pre) - 1
                if selection:
                    cursor = selection[0]
                    s = s_pre + s_post
                else:
                    s = s_pre[:-1] + s_post
                selection = None

            # Paste
            if cls._input_paste():
                focused_time = 0
                pasted_text = Clipboard.get_text()
                cursor = len(s_pre) + len(pasted_text)
                s = s_pre + pasted_text + s_post
                selection = None

            # Text input
            if text_input := cls._get_input_text(multiline):
                focused_time = 0
                cursor = len(s_pre) + len(text_input)
                s = s_pre + text_input + s_post
                selection = None

            # Backspace
            if cls._input_backspace():
                focused_time = 0
                cursor = len(s_pre) - 1
                if selection:
                    cursor = selection[0]
                    s = s_pre + s_post
                else:
                    s = s_pre[:-1] + s_post
                selection = None

            # Delete
            if cls._input_delete():
                focused_time = 0
                if selection:
                    cursor = selection[0]
                    s = s_pre + s_post
                else:
                    s = s_pre + s_post[1:]
                selection = None

            # Revert the changes if the text doesn't match the regex
            if regex:
                if not re.fullmatch(regex, s):
                    cursor = old_cursor
                    s = old_s
                    selection = old_selection

            # Clamp the cursor position
            cursor = pmath.clamp(cursor, 0, len(s))

            # Update history
            if old_s != s:
                redo_queue.clear()
                undo_queue.append((old_s, old_cursor))

            # Undo
            if cls._input_undo():
                try:
                    undo_text, undo_cursor = undo_queue.pop()
                    redo_queue.append((old_s, cursor))
                    s = undo_text
                    cursor = undo_cursor
                    selection = None
                except IndexError:
                    pass

            # Redo
            if cls._input_redo():
                try:
                    redo_text, redo_cursor = redo_queue.pop()
                    undo_queue.append((old_s, cursor))
                    s = redo_text
                    cursor = redo_cursor
                    selection = None
                except IndexError:
                    pass

            # Update the text
            text.text = s

            # Scroll to keep the cursor in focus
            if cls._is_input_navigation_key_pressed() or new_cursor != old_cursor or old_s != s:
                text_position = Point(content_rect.x - scroll_x, content_rect.y - scroll_y)
                cursor_position = cls._get_input_cursor_position(text_position, text, cursor)

                if cursor_position.x > content_rect.right():
                    scroll_x += (cursor_position.x - content_rect.right()) + text.font.line_height
                elif cursor_position.x < content_rect.left():
                    scroll_x -= (content_rect.left() - cursor_position.x) + text.font.line_height

                if cursor_position.y + text.font.line_height > content_rect.bottom():
                    scroll_y += (cursor_position.y - content_rect.bottom()) + text.font.line_height
                elif cursor_position.y < content_rect.top():
                    scroll_y -= (content_rect.top() - cursor_position.y) + text.font.line_height

        # Handle scrolling
        scroll_x_max = text.width - content_rect.width + 1
        scroll_y_max = text.height - content_rect.height

        # Create scroll bars
        if multiline:
            if horizontal_scroll_bar_rect:
                cls.save_cursor()
                cls.set_cursor(horizontal_scroll_bar_rect.x, horizontal_scroll_bar_rect.y)
                scroll_x = cls._horizontal_scroll_bar(
                    f"{name}__HorizontalScrollBar",
                    horizontal_scroll_bar_rect.width,
                    scroll_x,
                    0,
                    scroll_x_max
                )
                cls.restore_cursor()

            if vertical_scroll_bar_rect:
                cls.save_cursor()
                cls.set_cursor(vertical_scroll_bar_rect.x, vertical_scroll_bar_rect.y)
                scroll_y = cls._vertical_scroll_bar(
                    f"{name}__VerticalScrollBar",
                    vertical_scroll_bar_rect.height,
                    scroll_y,
                    0,
                    scroll_y_max
                )
                cls.restore_cursor()

            # Scroll with mouse wheel
            if widget['hovered']:
                if cls._mouse_scroll_wheel:
                    if Keyboard.get_shift():
                        scroll_x -= cls._mouse_scroll_wheel
                    else:
                        scroll_y -= cls._mouse_scroll_wheel

        # Constrain the scroll amount so that it can't scroll past the boundaries
        scroll_x = pmath.clamp(scroll_x, 0, scroll_x_max)
        scroll_y = pmath.clamp(scroll_y, 0, scroll_y_max)

        # Update data
        data['s'] = s
        data['focused'] = focused
        data['focused_time'] = focused_time
        data['cursor'] = cursor
        data['selection'] = selection
        data['scroll_x'] = scroll_x
        data['scroll_y'] = scroll_y
        data['undo_queue'] = undo_queue
        data['redo_queue'] = redo_queue

        # Start a sub-region, just for the clipping rect
        with cls.sub_region(content_rect):

            # Get text position
            text_position = Point(content_rect.x - scroll_x, content_rect.y - scroll_y)

            # Draw selection
            if selection:
                for i in range(selection[0], selection[1] + 1):
                    glyph = text.glyph(i)
                    glyph_rect = text.glyph_rect(glyph)
                    selection_rect = Rect(
                        glyph_rect.x + text_position.x,
                        glyph_rect.y + text_position.y,
                        glyph_rect.width,
                        glyph_rect.height
                    )
                    selection_rect.draw(cls._camera, cls.style("input_selection"), solid=True)

            # Draw text
            text.draw(cls._camera, text_position)

            # Draw cursor
            if data['focused']:
                blink = (focused_time // INPUT_CURSOR_BLINK_SPEED) % 2 == 0
                if blink:
                    cursor_position = cls._get_input_cursor_position(text_position, text, cursor)
                    cursor_a = cursor_position
                    cursor_b = cursor_position + Point(0, text.font.line_height - 1)
                    cursor_line = Line(cursor_a, cursor_b)
                    cursor_line.draw(cls._camera, cls.style("input_cursor"))

        return text.text

    @classmethod
    def _get_input_cursor_position(cls, text_position: Point, text: Text, cursor: int) -> Point:
        """ Get the position of the input cursor. """
        if not text.text:
            return text_position
        else:
            glyph = text.glyph(cursor)
            return text_position + text.glyph_position(glyph)

    @classmethod
    def _get_input_text(cls, multiline: bool) -> str:
        """ Get input characters that were typed this frame. """
        if text_input := InputManager.get_text_input():
            return text_input
        elif Keyboard.get_key_down(Keyboard.RETURN) or InputManager.get_key_repeat(Keyboard.RETURN):
            return "\n"
        elif Keyboard.get_key_down(Keyboard.KEYPAD_ENTER) or InputManager.get_key_repeat(Keyboard.KEYPAD_ENTER):
            return "\n"
        if multiline and (Keyboard.get_key_down(Keyboard.TAB) or InputManager.get_key_repeat(Keyboard.TAB)):
            return "    "

        return ""

    @classmethod
    def _input_return(cls) -> bool:
        """ Returns True if the Return or Enter key was pressed. """
        return Keyboard.get_key_down(Keyboard.RETURN) or Keyboard.get_key_down(Keyboard.KEYPAD_ENTER)

    @classmethod
    def _input_copy(cls) -> bool:
        """ Returns True if the Copy hotkey was pressed. """
        return Keyboard.get_ctrl() and Keyboard.get_key_down(Keyboard.C)

    @classmethod
    def _input_cut(cls) -> bool:
        """ Returns True if the Cut hotkey was pressed. """
        return Keyboard.get_ctrl() and Keyboard.get_key_down(Keyboard.X)

    @classmethod
    def _input_paste(cls) -> bool:
        """ Returns True if the Paste hotkey was pressed. """
        return Keyboard.get_ctrl() and (Keyboard.get_key_down(Keyboard.V) or InputManager.get_key_repeat(Keyboard.V))

    @classmethod
    def _input_undo(cls) -> bool:
        """ Returns True if the Undo hotkey was pressed. """
        z = Keyboard.get_key_down(Keyboard.Z) or InputManager.get_key_repeat(Keyboard.Z)
        return Keyboard.get_ctrl() and not Keyboard.get_shift() and z

    @classmethod
    def _input_redo(cls) -> bool:
        """ Returns True if the Redo hotkey was pressed. """
        z = Keyboard.get_key_down(Keyboard.Z) or InputManager.get_key_repeat(Keyboard.Z)
        return Keyboard.get_ctrl() and Keyboard.get_shift() and z

    @classmethod
    def _input_backspace(cls) -> bool:
        """ Returns True if the backspace key was pressed. """
        return Keyboard.get_key_down(Keyboard.BACKSPACE) or InputManager.get_key_repeat(Keyboard.BACKSPACE)

    @classmethod
    def _input_delete(cls) -> bool:
        """ Returns True if the delete key was pressed. """
        return Keyboard.get_key_down(Keyboard.DELETE) or InputManager.get_key_repeat(Keyboard.DELETE)
    
    @classmethod
    def _get_input_cursor_keyboard_movement(cls, text: Text, cursor: int, selection: tuple[int, int] | None) -> int:
        """ Get input cursor movement from the keyboard (arrow keys, home/end, etc). """
        # If there is no text, the cursor can't move
        s = text.text
        if not s:
            return cursor

        # Get current glyph
        glyph = text.glyph(cursor)

        # Conditionally, some inputs may act as other inputs.
        # For example, pressing the Up Arrow on the first line acts as the home key.
        # We store those as flags, so that we can treat them as those key presses later.
        home = False
        end = False

        # Left
        if Keyboard.get_key_down(Keyboard.LEFT_ARROW) or InputManager.get_key_repeat(Keyboard.LEFT_ARROW):
            if selection and not Keyboard.get_shift():
                cursor = selection[0]
            else:
                cursor -= 1

        # Right
        if Keyboard.get_key_down(Keyboard.RIGHT_ARROW) or InputManager.get_key_repeat(Keyboard.RIGHT_ARROW):
            if selection and not Keyboard.get_shift():
                cursor = selection[1] + 1
            else:
                cursor += 1

        # Up
        if Keyboard.get_key_down(Keyboard.UP_ARROW) or InputManager.get_key_repeat(Keyboard.UP_ARROW):
            if glyph.line == 0:
                home = True
            else:
                previous_line_start = text.line_start(glyph.line-1)
                previous_line_end = text.line_end(glyph.line-1)
                column = glyph.column
                cursor = pmath.clamp(previous_line_start + column, previous_line_start, previous_line_end)

        # Down
        if Keyboard.get_key_down(Keyboard.DOWN_ARROW) or InputManager.get_key_repeat(Keyboard.DOWN_ARROW):
            if glyph.line == text.lines - 1:
                end = True
            else:
                next_line_start = text.line_start(glyph.line + 1)
                next_line_end = text.line_end(glyph.line + 1)
                column = glyph.column
                cursor = pmath.clamp(next_line_start + column, next_line_start, next_line_end)

        # Home
        if Keyboard.get_key_down(Keyboard.HOME) or home:
            line_start = text.line_start(glyph.line)
            cursor = line_start

        # End
        if Keyboard.get_key_down(Keyboard.END) or end:
            line_end = text.line_end(glyph.line)
            cursor = line_end

        # Clamp cursor range
        cursor = pmath.clamp(cursor, 0, len(s))

        return cursor

    @classmethod
    def _get_input_cursor_mouse_movement(cls, text: Text, cursor: int, mouse_position: Point) -> int:
        """ Get input cursor movement from the mouse. """
        if not Mouse.get_left_mouse():
            return cursor

        # Get the line that the mouse is on
        line = pmath.clamp(mouse_position.y // text.font.line_height, 0, text.lines - 1)
        line_start = text.line_start(line)
        line_end = text.line_end(line)

        # If the mouse is on a glyph, use that glyph's index.
        # If the mouse's X position is past the center point of a glyph, use the next glyph instead.
        if glyph := text.glyph_at(mouse_position):
            if mouse_position.x >= text.glyph_rect(glyph).center().x:
                cursor = glyph.index + 1
            else:
                cursor = glyph.index
            return pmath.clamp(cursor, line_start, line_end)

        # If the mouse Y position is above the text, put it on the first line
        elif mouse_position.y < 0:
            return 0

        # If the mouse X position is less than zero, get the first glyph index on the line
        elif mouse_position.x < 0:
            return line_start

        # If we still don't have a cursor, then we must be past the last glyph, so get the last glyph index on the line
        else:
            if line == text.lines - 1:
                return text.end_glyph().index
            else:
                return line_end

    @classmethod
    def _update_input_selection(cls, text: Text, old_cursor: int, new_cursor: int, selection: tuple[int, int] | None) -> tuple[int, int] | None:  # noqa
        """ Get the selection input.
        If any characters are selected, returns a tuple of (first_selected_char, last_selected_char), inclusive.
        If no characters are selected, returns None.
        """
        # Clear the selection if a navigation button was pressed without Shift held.
        # Sometimes navigation buttons can be pressed without actually moving the cursor (like pressing Right Arrow at
        #   the end of the text). In those cases, we still want to clear the selection, even if the cursor didn't move.
        if not Keyboard.get_shift() and cls._is_input_navigation_key_pressed():
            return None

        # Select all
        if Keyboard.get_key_down(Keyboard.A) and Keyboard.get_ctrl():
            return 0, len(text.text) - 1

        # Deselect all
        if Keyboard.get_key_down(Keyboard.ESCAPE):
            return None

        # Clear the selection if the mouse was clicked without the shift key held
        if cls._left_mouse_pressed and not Keyboard.get_shift():
            return None

        # Do nothing if the cursor hasn't moved
        if old_cursor == new_cursor:
            return selection

        # Clear the selection if we weren't dragging the mouse or if Shift was not held.
        if not Keyboard.get_shift() and not Mouse.get_left_mouse():
            return None

        # If there was no current selection, the new selection is in between the cursor movement
        if not selection:
            return min(old_cursor, new_cursor), max(old_cursor, new_cursor) - 1

        # At this point, the only scenario left to handle is updating an existing selection
        # Cursor moves right
        if new_cursor > old_cursor:
            # Selection is left-to-right, cursor was at end of selection, cursor moves right
            if old_cursor == selection[1] + 1:
                return selection[0], new_cursor - 1

            # Selection is right-to-left, cursor was at beginning of selection, cursor moves within selection range
            elif new_cursor <= selection[1]:
                return new_cursor, selection[1]

            # Selection is right-to-left, cursor was at beginning of selection, cursor moves to selection end
            elif new_cursor == selection[1] + 1:
                return None

            # Selection is right-to-left, cursor was at beginning of selection, cursor moves past end of selection
            else:
                return selection[1] + 1, new_cursor - 1

        # Cursor moves left
        else:
            # Selection is right-to-left, cursor was at beginning of selection, cursor moves left
            if old_cursor == selection[0]:
                return new_cursor, selection[1]

            # Selection is left-to-right, cursor was at end of selection, cursor moves within selection range
            elif new_cursor > selection[0]:
                return selection[0], new_cursor - 1

            # Selection is left-to-right, cursor was at end of selection, cursor moves to selection beginning
            elif new_cursor == selection[0]:
                return None

            # Selection is left-to-right, cursor was at end of selection, cursor moves past beginning of selection
            else:
                return new_cursor, selection[0] - 1

    @classmethod
    def _is_input_navigation_key_pressed(cls) -> bool:
        """ Returns True if an input navigation key was pressed. """
        if (
                Keyboard.get_key_down(Keyboard.UP_ARROW) or
                Keyboard.get_key_down(Keyboard.DOWN_ARROW) or
                Keyboard.get_key_down(Keyboard.LEFT_ARROW) or
                Keyboard.get_key_down(Keyboard.RIGHT_ARROW) or
                Keyboard.get_key_down(Keyboard.HOME) or
                Keyboard.get_key_down(Keyboard.END)
        ):
            return True
        else:
            return False

    @classmethod
    def _scroll_area_rects(cls,
                           scroll_area_rect: Rect,
                           content_width: int,
                           content_height: int,
                           force_horizontal: bool | None,
                           force_vertical: bool | None,
                           ) -> tuple[Rect, Rect | None, Rect | None]:
        """ Get the rects for a scroll area widget.
        `force_horizontal` and `force_vertical` determine the visibility of the scroll bars for each axis:
            If None (the default), the visibility is calculated based on whether or not the content fits the scroll area
            If True, the bar is always visible
            If False, the bar is never visible

        Returns a tuple of (content_area_rect, horizontal_bar_rect, vertical_bar_rect).
        If the horizontal or vertical bar rects are not visible, None will be returned instead of a rect.
        """
        # Start calculating the content area
        x = scroll_area_rect.x
        y = scroll_area_rect.y
        width = scroll_area_rect.width
        height = scroll_area_rect.height

        content_area_x = x + SCROLL_AREA_CONTENT_PADDING
        content_area_y = y + SCROLL_AREA_CONTENT_PADDING
        content_area_width = width - SCROLL_AREA_CONTENT_PADDING * 2
        content_area_height = height - SCROLL_AREA_CONTENT_PADDING * 2

        # Calculate scroll bar geometry
        horizontal_bar_x = x
        horizontal_bar_y = scroll_area_rect.bottom() - SCROLL_BAR_THICKNESS + 1
        horizontal_bar_width = width
        horizontal_bar_height = SCROLL_BAR_THICKNESS

        vertical_bar_x = scroll_area_rect.right() - SCROLL_BAR_THICKNESS + 1
        vertical_bar_y = y
        vertical_bar_width = SCROLL_BAR_THICKNESS
        vertical_bar_height = height

        # Check initial scroll bar visibility
        # This checks each axis independently
        if force_horizontal is None:
            if content_width > content_area_width:
                horizontal_bar_visible = True
            else:
                horizontal_bar_visible = False
        else:
            horizontal_bar_visible = force_horizontal

        if force_vertical is None:
            if content_height > content_area_height:
                vertical_bar_visible = True
            else:
                vertical_bar_visible = False
        else:
            vertical_bar_visible = force_vertical

        # Because the vertical scroll bar affects the available horizontal space, and the horizontal scroll bar
        #   affects the vertical space, we need to do a follow-up check to see if enabling either scroll bar caused
        #   the opposite axis to run out of space.
        if force_vertical is None and horizontal_bar_visible:
            if content_height > content_area_height - horizontal_bar_height:
                vertical_bar_visible = True
            else:
                vertical_bar_visible = False

        if force_horizontal is None and vertical_bar_visible:
            if content_width > content_area_width - vertical_bar_width:
                horizontal_bar_visible = True
            else:
                horizontal_bar_visible = False

        # Adjust the scroll bar lengths so that they don't overlap
        if horizontal_bar_visible and vertical_bar_visible:
            horizontal_bar_width -= SCROLL_BAR_THICKNESS
            vertical_bar_height -= SCROLL_BAR_THICKNESS

        # Adjust the content area, accounting for the scroll bar visibility
        if vertical_bar_visible:
            content_area_width -= vertical_bar_width

        if horizontal_bar_visible:
            content_area_height -= horizontal_bar_height

        # Calculate the final rects
        content_rect = Rect(content_area_x, content_area_y, content_area_width, content_area_height)

        if horizontal_bar_visible:
            horizontal_bar_rect = Rect(horizontal_bar_x, horizontal_bar_y, horizontal_bar_width, horizontal_bar_height)
        else:
            horizontal_bar_rect = None

        if vertical_bar_visible:
            vertical_bar_rect = Rect(vertical_bar_x, vertical_bar_y, vertical_bar_width, vertical_bar_height)
        else:
            vertical_bar_rect = None

        return content_rect, horizontal_bar_rect, vertical_bar_rect

    @classmethod
    def _horizontal_scroll_bar(cls, name: str, width: int, value: int, minimum: int, maximum: int) -> int:
        """ Create a horizontal scroll bar widget.
        Value is the amount scrolled between the start and end value.
        The size of the handle is automatically calculated based on the ratio of the min/max values to the width.
        Returns the new scroll value.
        """
        # Enforce minimum size
        if width < SCROLL_BAR_MINIMUM_LENGTH * 2:
            width = SCROLL_BAR_MINIMUM_LENGTH * 2

        # Draw background
        background_rect = Rect(cls._cx, cls._cy, width, SCROLL_BAR_THICKNESS)
        Renderer.draw_rounded_rect_solid(background_rect, SCROLL_BAR_RADIUS, cls.style("scroll_bar_background"))

        # Calculate handle size
        scale = (maximum + width - minimum) / width
        if scale > 1:
            handle_width = width // scale
        else:
            handle_width = width

        # Prevent the scroll bar from being too small
        if handle_width < SCROLL_BAR_MINIMUM_LENGTH:
            handle_width = SCROLL_BAR_MINIMUM_LENGTH

        # Calculate the range of motion for the scroll bar
        # This is the maximum amount of pixels the scroll bar can move
        bar_range = width - handle_width

        # Get scroll amount expressed as a percentage
        try:
            value = pmath.clamp(value, minimum, maximum)
            percent = value / (maximum - minimum)
        except ZeroDivisionError:
            percent = 0

        # Calculate position based on the scroll amount
        offset = percent * bar_range
        x = background_rect.x + offset
        y = background_rect.y
        cls.set_cursor(x, y)

        # Create widget
        widget = cls.widget(name, handle_width, SCROLL_BAR_THICKNESS)

        # Scroll bar color
        if cls.disabled():
            color = cls.style("scroll_bar_disabled")
        elif widget['held'] or widget['dragged']:
            color = cls.style("scroll_bar_pressed")
        elif widget['hovered']:
            color = cls.style("scroll_bar_hovered")
        else:
            color = cls.style("scroll_bar")

        # Draw scroll bar
        Renderer.draw_rounded_rect_solid(widget['rect'],  SCROLL_BAR_RADIUS, color)

        # Drag scroll
        if widget['dragged']:
            if bar_range == 0:
                value = 0
            else:
                original_offset = widget['drag_start'].x - background_rect.x
                new_offset = original_offset + cls._mouse_drag_delta.x
                new_percent = new_offset / bar_range
                value = int((maximum - minimum) * new_percent)

        # Update cursor
        cls._update_cursor_after_placement(background_rect)

        # Clamp value
        value = pmath.clamp(value, minimum, maximum)
        return value

    @classmethod
    def _vertical_scroll_bar(cls, name: str, height: int, value: int, minimum: int, maximum: int) -> int:
        """ Create a vertical scroll bar widget.
        Value is the amount scrolled between the start and end value.
        The size of the handle is automatically calculated based on the ratio of the min/max values to the height.
        Returns the new scroll value.
        """
        # Enforce minimum size
        if height < SCROLL_BAR_MINIMUM_LENGTH * 2:
            height = SCROLL_BAR_MINIMUM_LENGTH * 2

        # Draw background
        background_rect = Rect(cls._cx, cls._cy, SCROLL_BAR_THICKNESS, height)
        Renderer.draw_rounded_rect_solid(background_rect, SCROLL_BAR_RADIUS, cls.style("scroll_bar_background"))

        # Calculate handle size
        scale = (maximum + height - minimum) / height
        if scale > 1:
            handle_height = height // scale
        else:
            handle_height = height

        # Prevent the scroll bar from being too small
        if handle_height < SCROLL_BAR_MINIMUM_LENGTH:
            handle_height = SCROLL_BAR_MINIMUM_LENGTH

        # Calculate the range of motion for the scroll bar
        # This is the maximum amount of pixels the scroll bar can move
        bar_range = height - handle_height

        # Get scroll amount expressed as a percentage
        try:
            value = pmath.clamp(value, minimum, maximum)
            percent = value / (maximum - minimum)
        except ZeroDivisionError:
            percent = 0

        # Calculate position based on the scroll amount
        offset = percent * bar_range
        x = background_rect.x
        y = background_rect.y + offset
        cls.set_cursor(x, y)

        # Create widget
        widget = cls.widget(name, SCROLL_BAR_THICKNESS, handle_height)

        # Scroll bar color
        if cls.disabled():
            color = cls.style("scroll_bar_disabled")
        elif widget['held'] or widget['dragged']:
            color = cls.style("scroll_bar_pressed")
        elif widget['hovered']:
            color = cls.style("scroll_bar_hovered")
        else:
            color = cls.style("scroll_bar")

        # Draw scroll bar
        Renderer.draw_rounded_rect_solid(widget['rect'], SCROLL_BAR_RADIUS, color)

        # Drag scroll
        if widget['dragged']:
            if bar_range == 0:
                value = 0
            else:
                original_offset = widget['drag_start'].y - background_rect.y
                new_offset = original_offset + cls._mouse_drag_delta.y
                new_percent = new_offset / bar_range
                value = int((maximum - minimum) * new_percent)

        # Update cursor
        cls._update_cursor_after_placement(background_rect)

        # Clamp value
        value = pmath.clamp(value, minimum, maximum)
        return value

    @classmethod
    def _update_cursor_after_placement(cls, rect: Rect) -> None:
        """ Update the cursor after placing a widget (or other widget-like UI item).
        `rect` is the rect of the item that was just placed.
        """
        if cls.layout() == LAYOUT_VERTICAL:
            cls.set_cursor(rect.x, rect.bottom() + cls._spacing_y)

        elif cls.layout() == LAYOUT_HORIZONTAL:
            cls.set_cursor(rect.right() + 1 + cls._spacing_x, rect.y)

        elif cls.layout() == LAYOUT_GRID:
            cls._grid_index += 1
            column = cls._grid_index % cls._grid_columns
            row = cls._grid_index // cls._grid_columns
            cls.set_cursor(
                cls._grid_x + column * (cls._grid_column_width + cls._spacing_x),
                cls._grid_y + row * (cls._grid_row_height + cls._spacing_y)
            )

        # Update bounding box calculation
        if cls._calculating_bbox:
            if cls._bbox_stack[-1]:
                x_min, x_max, y_min, y_max = cls._bbox_stack[-1]
                if rect.x < x_min:
                    cls._bbox_stack[-1][0] = rect.x
                if rect.right() > x_max:
                    cls._bbox_stack[-1][1] = rect.right()
                if rect.y < y_min:
                    cls._bbox_stack[-1][2] = rect.y
                if rect.bottom() > y_max:
                    cls._bbox_stack[-1][3] = rect.bottom()
            else:
                cls._bbox_stack[-1] = [rect.x, rect.right(), rect.y, rect.bottom()]
