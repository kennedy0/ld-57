from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Frame:
    """ A  rectangular region in an atlas that contains information about a sprite that was packed. """

    # The name of the frame
    name: str

    # Original sprite size
    sprite_width: int
    sprite_height: int

    # The sprite's top-left pixel offset in the original canvas (prior to trimming transparency)
    offset_x: int
    offset_y: int

    # Frame width after trimming transparent edges
    frame_width: int
    frame_height: int

    # Frame position on the atlas
    x: int
    y: int

    # Extra metadata
    metadata: dict[str, Any]

    def __str__(self) -> str:
        return f"Frame({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def from_dict(cls, d: dict) -> Frame:
        """ Read a dictionary to get frame values. """
        name = d['name']
        sprite_width = d['sprite_width']
        sprite_height = d['sprite_height']
        offset_x = d['offset_x']
        offset_y = d['offset_y']
        frame_width = d['frame_width']
        frame_height = d['frame_height']
        x = d['x']
        y = d['y']
        metadata = d.get('metadata', {})

        return cls(name, sprite_width, sprite_height, offset_x, offset_y, frame_width, frame_height, x, y, metadata)
