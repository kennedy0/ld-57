from __future__ import annotations

from potion.frame import Frame
from potion.log import Log
from potion.time import Time


class Animation:
    """ Stores frame data and playback information about an animation. """
    def __init__(self, name: str) -> None:
        self._name = name
        self._loop = True
        self._is_playing = False
        self._frame = 1
        self._frame_changed = False
        self._duration = 0.0

        # A list of frames that belong to the animation
        self._frames: list[Frame] = []
        self._durations: list[float] = []

        # The elapsed time since the current frame has started playing
        self._elapsed_time_ms = 0

    def __str__(self) -> str:
        return f"Animation({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """ The name of the animation. """
        return self._name

    @property
    def loop(self) -> bool:
        """ If True, the animation will loop when it's finished playing. """
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    @property
    def is_playing(self) -> bool:
        """ Whether or not the animation is currently playing. """
        return self._is_playing

    @property
    def frame(self) -> int:
        """ The current frame number of the animation. This always starts at 1. """
        return self._frame

    @property
    def frame_changed(self) -> bool:
        """ If True, the current frame just changed.
        This is useful for triggering effects when a specific frame of animation starts playing.
        """
        return self._frame_changed

    @property
    def duration(self) -> float:
        """ Get the total duration (in milliseconds) of the animation.
        This value can be a float if any frames have non-integer durations (e.g. scaled animations).
        """
        return self._duration

    @property
    def frame_count(self) -> int:
        """ The number of frames in the animation. """
        return len(self._frames)

    @classmethod
    def empty(cls) -> Animation:
        """ Create an empty animation. """
        animation = cls("empty-animation")
        animation.add_frame(
            Frame(
                name="empty",
                sprite_width=0,
                sprite_height=0,
                offset_x=0,
                offset_y=0,
                frame_width=0,
                frame_height=0,
                x=0,
                y=0,
                metadata={'duration': 0}
            )
        )
        return animation

    def get_frame(self, frame_number: int) -> Frame:
        """ Get a frame from this animation. """
        return self._frames[frame_number-1]

    def add_frame(self, frame: Frame) -> None:
        """ Add a frame to this animation. """
        duration = frame.metadata.get('duration')
        if duration is None:
            duration = 100
            Log.warning(f"{frame} has no 'duration' in metadata - its duration will be set to {duration}.")

        self._frames.append(frame)
        self._durations.append(duration)
        self._duration += duration

    def add_frames(self, frames: list[Frame]) -> None:
        """ Add frames to this animation. """
        for frame in frames:
            self.add_frame(frame)

    def get_frame_duration(self, frame_number: int) -> float:
        """ Get the duration (in milliseconds) of a specific frame. """
        return self._durations[frame_number-1]

    def set_frame_duration(self, frame_number: int, duration: float) -> None:
        """ Set the duration (in milliseconds) of a specific frame. """
        if duration < 0:
            Log.error(f"Frame duration cannot be negative (got {duration})")
            return

        if frame_number < 1 or frame_number > self.frame_count:
            Log.error(f"{self} has no frame number {frame_number}")
            return

        self._durations[frame_number-1] = duration
        self._duration = int(sum(self._durations))

    def set_duration(self, duration: float, uniform: bool = False) -> None:
        """ Set the total duration (in milliseconds) of the animation.

        If 'uniform' is True, the duration will be evenly spread across all the frames, and the original timing will
            not be respected.
        """
        if uniform:
            self._durations = [duration / self.frame_count] * self.frame_count
        else:
            for i in range(self.frame_count):
                d_percent = self._durations[i] / self._duration
                self._durations[i] = duration * d_percent

        # Set the new total duration
        self._duration = duration

    def play(self) -> None:
        """ Play the animation. """
        self._is_playing = True

    def pause(self) -> None:
        """ Pause the animation. """
        self._is_playing = False

    def stop(self) -> None:
        """ Stop and rewind the animation. """
        self._is_playing = False
        self.rewind()

    def rewind(self) -> None:
        """ Rewind the animation back to the beginning. """
        self._frame = 1
        self._elapsed_time_ms = 0

    def set_frame(self, frame: int) -> None:
        """ Set the frame that is currently playing. """
        if frame < 1:
            Log.error(f"Error setting frame {frame} on {self}: frame cannot be less than 1")
            return

        if frame > self.frame_count:
            Log.error(
                f"Error setting frame {frame} on {self}: there are only {self.frame_count} frames in the animation"
            )
            return

        self._frame = frame
        self._elapsed_time_ms = 0

    def update(self) -> None:
        """ Update the time and current frame. """
        # Do nothing if the animation isn't playing
        if not self.is_playing:
            return

        if self._elapsed_time_ms == 0:
            self._frame_changed = True
        else:
            self._frame_changed = False

        # Advance time
        self._elapsed_time_ms += Time.delta_time_ms

        # Check if the current frame should be advanced
        current_frame_duration = self.get_frame_duration(self.frame)
        while self._elapsed_time_ms > current_frame_duration:
            # Update the current frame time and number
            self._elapsed_time_ms -= current_frame_duration
            self._frame += 1
            self._frame_changed = True

            # Handle case where we reached the end of the animation
            if self.frame > self.frame_count:
                if self._loop:
                    # If the animation loops, put the frame number back to 1
                    self._frame = 1
                else:
                    # If the animation doesn't loop, stop playing
                    self._is_playing = False
                    self._frame_changed = False
                    self._frame = self.frame_count
                    break

            # Get the new current frame duration
            current_frame_duration = self.get_frame_duration(self.frame)
