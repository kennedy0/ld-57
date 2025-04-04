from __future__ import annotations

from potion.animation import Animation
from potion.atlas import Atlas
from potion.log import Log
from potion.sprite import Sprite


class AnimatedSprite(Sprite):
    """ A sprite that contains one or more animations. """
    def __init__(self, content_path: str) -> None:
        """ `content_path` is the path to the sprite atlas texture file. """
        super().__init__(content_path)
        self._animation = None
        self._current_animation = Animation.empty()

        # A list of animations that belong to the sprite
        self._animations: dict[str, Animation] = {}

    @property
    def animation(self) -> str | None:
        """ The name of the animation that is currently playing. """
        return self._animation

    @property
    def frame(self) -> int:
        """ The frame number of the current animation. """
        return self._current_animation.frame

    @property
    def is_playing(self) -> bool:
        """ If True, the current animation is playing.
        Will return False if there is no animation.
        """
        return self._current_animation.is_playing

    @classmethod
    def from_atlas(cls, content_path: str, sprite_name: str) -> AnimatedSprite:
        """ Factory method to create a sprite from an atlas.
        `content_path` is the path to the sprite atlas texture file.
        """
        # Create sprite
        sprite = cls(content_path)
        sprite._name = sprite_name

        # Create atlas
        atlas = Atlas.instance(content_path)

        # Get animation data from atlas
        animation_names = atlas.animations(sprite_name)

        # Return an empty sprite
        if not animation_names:
            Log.error(f"No animations exist for {sprite}; creating an empty sprite instead")
            return cls.empty()

        # Add animations to sprite
        for animation_name in animation_names:
            animation = Animation(animation_name)
            frames = atlas.animation_frames(sprite_name, animation_name)
            animation.add_frames(frames)
            sprite.add_animation(animation)

        # Initialize frame data from the first frame
        sprite._apply_frame_data(sprite.get_animation('default').get_frame(1))

        return sprite

    @classmethod
    def empty(cls) -> AnimatedSprite:
        """ Create an empty sprite with no texture. """
        return cls("empty-sprite")

    def get_animation(self, animation_name: str) -> Animation | None:
        """ Get an animation in this sprite. """
        animation = self._animations.get(animation_name)
        if not animation:
            Log.error(f"{self} does not have an animation named {animation_name}")
            return None

        return animation

    def add_animation(self, animation: Animation) -> None:
        """ Add an animation to this sprite. """
        if animation.name in self._animations:
            Log.error(f"{self} already has an animation named {animation.name}")
            return

        self._animations[animation.name] = animation

    def play(self, animation_name: str) -> None:
        """ Play an animation. """
        # Get the new animation
        new_animation = self.get_animation(animation_name)
        if not new_animation:
            return

        # If a new animation name was provided, set the current animation to that.
        if animation_name != self.animation:
            # Stop the current animation
            self._current_animation.stop()

            # Set the new animation
            self._animation = animation_name
            self._current_animation = new_animation

            # Rewind the new animation, so it starts from the first frame
            new_animation.rewind()

        # Play the animation
        new_animation.play()
        self._apply_frame_data_from_current_animation()

    def pause(self) -> None:
        """ Pause the current animation. """
        self._current_animation.pause()

    def stop(self) -> None:
        """ Stop the current animation. """
        self._current_animation.stop()
        self._apply_frame_data_from_current_animation()

    def rewind(self) -> None:
        """ Rewind the current animation. """
        self._current_animation.rewind()
        self._apply_frame_data_from_current_animation()

    def set_frame(self, frame: int) -> None:
        """ Set the frame that is currently playing. """
        self._current_animation.set_frame(frame)
        self._apply_frame_data_from_current_animation()

    def frame_started(self, frame: int) -> bool:
        """ Check if a specific frame of the current animation has just started. """
        if self._current_animation.frame_changed and self._current_animation.frame == frame:
            return True

        return False

    def update(self) -> None:
        """ Update the current animation. """
        if not self.animation:
            return

        # Get the frame before updating
        frame_pre_update = self._current_animation.frame

        # Advance time
        self._current_animation.update()

        # If the frame number has changed, we need to update the sprite
        if self._current_animation.frame != frame_pre_update:
            self._apply_frame_data_from_current_animation()

    def _apply_frame_data_from_current_animation(self) -> None:
        """ Use the current animation to apply frame data """
        self._apply_frame_data(self._current_animation.get_frame(self._current_animation.frame))
