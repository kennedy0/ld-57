from __future__ import annotations

import json

from potion.content import Content
from potion.data_types.blend_mode import BlendMode
from potion.frame import Frame
from potion.log import Log


"""
SpriteTagList: Stores lists of frames associated with each tag.
{
    'SpriteName1': {
        'TagName1': [
            [Frame1, Frame2, Frame3]
        ],
        'TagName2': [
            [Frame11, Frame12, Frame13],
            [Frame20, Frame21, Frame22]
        ]
    }
}
"""
SpriteTagList = dict[str, dict[str, list[list[Frame]]]]

"""
SpriteAnimationList: Stores a list of frames that are part of an animated sprite.
{
    'SpriteName1': {
        'default': [Frame1, Frame2, ...],  # 'default' always exists as an animation with all frames
        'AnimationName1': [Frame1, Frame2, ...],
        'AnimationName2': [Frame1, Frame2, ...],
    },
}
"""
SpriteAnimationList = dict[str, dict[str, list[Frame]]]


class Atlas:
    """ A single texture that has multiple sprites packed inside it.
    The data needed to recreate the original textures are stored in frames.
    """

    __instances: dict[str, Atlas] = {}

    def __init__(self, content_path: str) -> None:
        """ `content_path` is the path to the frame data file. """
        self._name = content_path
        self._texture = Content.load_texture(content_path)
        self._frames: dict[str, Frame] = {}
        self._sprite_tags: SpriteTagList = {}
        self._sprite_animations: SpriteAnimationList = {}

        self._init_frames(content_path)
        self._init_animations()

    def __str__(self) -> str:
        return f"Atlas({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """ The name of the atlas. """
        return self._name

    @property
    def frames(self) -> list[Frame]:
        """ Get a list of all frames in the atlas. """
        return list(self._frames.values())

    @property
    def frame_names(self) -> list[str]:
        """ Get a list of all frame names in the atlas. """
        return list(self._frames.keys())

    @property
    def sprites(self) -> list[str]:
        """ Get a list of all sprite names in the atlas. """
        return list(self._sprite_animations.keys())

    @classmethod
    def instance(cls, content_path: str) -> Atlas:
        """ Get or create a new atlas font.
        This should almost always be used instead of instantiating creating a new Atlas object, because it is expensive.

        `content_path` is the path to the frame data file.
        """
        # Get atlas from instance cache if it exists
        if atlas := cls.__instances.get(content_path):
            return atlas

        # Create and cache new atlas
        atlas = Atlas(content_path)
        cls.__instances[content_path] = atlas
        return atlas

    def _init_frames(self, content_path: str) -> None:
        """ Initialize frames by reading frame data file.
        `content_path` is the path to the frame data file.
        """
        # Get path to framedata file
        framedata_file = Content.with_suffix(content_path, ".framedata")

        # Make sure framedata file exists
        if not Content.is_file(framedata_file):
            raise FileNotFoundError(f"Could not find framedata file: {framedata_file}")

        # Read frame data from file
        with Content.open(framedata_file) as fp:
            frame_data: dict = json.load(fp)

        # Create frames from frame data
        for frame_name, frame_dict in frame_data.items():
            self.add_frame(Frame.from_dict(frame_dict))

    def _init_animations(self) -> None:
        """ Populate animated sprite info from frame data. """
        # Initialize sprite animation dict with the default animation
        for _, frame in self._frames.items():
            sprite_name = frame.metadata.get('sprite_name')
            if not sprite_name:
                continue
            elif sprite_name not in self._sprite_animations:
                self._sprite_animations[sprite_name] = {'default': []}

            self._sprite_animations[sprite_name]['default'].append(frame)

        # Populate the rest of the animation data (if any) based on the source format
        for sprite in self._sprite_animations.keys():
            first_frame = self._sprite_animations[sprite]['default'][0]
            source_format = first_frame.metadata.get('source_format')
            if source_format == "aseprite":
                self._init_aseprite_animations(sprite)

        # Sort all animations by their frame number
        for _, animation_dict in self._sprite_animations.items():
            for _, frames in animation_dict.items():
                frame_list: list[Frame] = frames
                frame_list.sort(key=lambda f: f.name)

    def _init_aseprite_animations(self, sprite_name: str) -> None:
        """ Populate animated sprite info from Aseprite frame data.
        Animations are created based on tags. Some common scenarios are described below:

        Ex 1:
        An animation is created for each tag.
        ┌─Idle──┐┌───Walk───┐
        [1][2][3][4][5][6][7]

        This example creates 2 animations:
            Idle (3 frames)
            Walk (4 frames)

        Ex 2:
        Tags can be partially or fully overlapping.
        ┌──────Jump──────┐
        ├─Rise──┐┌─Fall──┼──┐
        [1][2][3][4][5][6][7]

        This example creates 3 animations:
            Jump (6 frames)
            Rise (3 frames)
            Fall (4 frames)

        Ex 3:
        Duplicate tags do not create animations.
        ┌─────Attack─────┐┌────────Hit────────┐
        ├─Start─┐┌─End───┤├─Start─┐┌──End─────┤
        [1][2][3][4][5][6][7][8][9][10][11][12]

        This creates 2 animations:
            Attack (6 frames)
            Hit (6 frames)
        """
        frames = self._sprite_animations[sprite_name]['default']

        # Build sprite tag list
        tags_last_frame = set()
        for frame in frames:
            # Initialize sprite tag list
            sprite_name = frame.metadata.get('sprite_name')
            if not sprite_name:
                continue
            elif sprite_name not in self._sprite_tags:
                self._sprite_tags[sprite_name] = {}

            # Get a list of tags for the current frame
            tags_this_frame = set(frame.metadata.get('tags', []))

            # Add tags to list
            for tag in tags_this_frame:
                # Start new range
                if tag not in tags_last_frame:
                    if tag not in self._sprite_tags[sprite_name]:
                        # Create a key for the tag if it doesn't exist
                        self._sprite_tags[sprite_name].update({tag: []})

                    # Add a new range to the existing tag key
                    self._sprite_tags[sprite_name][tag].append([])

                # Add the new frame
                self._sprite_tags[sprite_name][tag][-1].append(frame)

            # Copy tag set for next frame
            tags_last_frame = tags_this_frame.copy()

        # Build sprite animation list for each unique tag
        for tag in self._sprite_tags[sprite_name]:
            frame_ranges = self._sprite_tags[sprite_name][tag]
            if len(frame_ranges) == 1:
                self._sprite_animations[sprite_name][tag] = frame_ranges[0].copy()

    def set_texture_blend_mode(self, blend_mode: BlendMode) -> None:
        """ Set the atlas's texture's blend mode. """
        self._texture.set_blend_mode(blend_mode)

    def add_frame(self, frame: Frame) -> None:
        """ Add a frame to the atlas. """
        if frame.name in self._frames:
            Log.error(f"Frame {frame.name} is already in the atlas.")
            return

        self._frames[frame.name] = frame

    def frame(self, frame_name: str) -> Frame:
        """ Get a frame from the atlas. """
        return self._frames[frame_name]

    def animations(self, sprite_name: str) -> list[str]:
        """ Get a list of animations for a given sprite. """
        animations = self._sprite_animations.get(sprite_name)
        if not animations:
            Log.error(f"'{sprite_name}' is not in the list of animated sprites for {self}.")
            return []

        return list(animations.keys())

    def animation_frames(self, sprite_name: str, animation_name: str) -> list[Frame]:
        """ Get a list of frames for a given sprite animation. """
        frames = self._sprite_animations.get(sprite_name, {}).get(animation_name)
        if not frames:
            Log.error(f"'{sprite_name}' sprite has no animation named {animation_name}")
            return []

        return frames
