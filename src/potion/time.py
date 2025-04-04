from __future__ import annotations

import sdl2.timer


class Time:
    """ Get time information from the engine. """

    # Number of milliseconds since SDL was initialized
    __ticks = 0
    __previous_ticks = 0

    # Engine fixed framerate
    __engine_framerate = 0

    # Time elapsed since the last frame
    delta_time_ms = 0
    delta_time = 0.0

    @classmethod
    def set_engine_framerate(cls, framerate: int) -> None:
        """ Set the framerate that the engine is running at. """
        cls.__engine_framerate = framerate

    @classmethod
    def update(cls) -> None:
        """ Update the time. """
        # Calculate the time since the previous update
        cls.__ticks = sdl2.timer.SDL_GetTicks64()
        cls.delta_time_ms = cls.__ticks - cls.__previous_ticks
        cls.__previous_ticks = cls.__ticks

        # Convert to seconds
        cls.delta_time = cls.delta_time_ms / 1000.0

    @classmethod
    def s_to_frames(cls, s: float) -> float:
        """ Convert seconds to frames. """
        return s * cls.__engine_framerate

    @classmethod
    def ms_to_frames(cls, ms: float) -> float:
        """ Convert milliseconds to frames. """
        return (ms / 1000) * cls.__engine_framerate

    @classmethod
    def frames_to_s(cls, frames: float) -> float:
        """ Convert frames to seconds. """
        return frames / cls.__engine_framerate

    @classmethod
    def frames_to_ms(cls, frames: float) -> float:
        """ Convert frames to milliseconds. """
        return frames * 1000 / cls.__engine_framerate
