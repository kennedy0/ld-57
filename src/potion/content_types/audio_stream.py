from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import IO

import sdl2.sdlmixer


class AudioStream:
    """ A wrapper around SDL_mixer Mix_Music.

    New instances of this shouldn't be created manually, instead the factory methods should be used to more easily
    initialize the audio stream.
    """
    def __init__(self, name: str, rw: sdl2.SDL_RWops, fp: IO | None = None) -> None:
        self._name = name
        self._rw = rw
        self._fp = fp
        self._sdl_mix_music = sdl2.sdlmixer.Mix_LoadMUS_RW(self._rw, freesrc=True)

    def __del__(self) -> None:
        sdl2.sdlmixer.Mix_FreeMusic(self._sdl_mix_music)
        if self._fp:
            self._fp.close()

    def __str__(self) -> str:
        return f"AudioStream({self._name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def sdl_mix_music(self) -> sdl2.sdlmixer.Mix_Music:
        return self._sdl_mix_music

    @classmethod
    def create_empty(cls) -> AudioStream:
        """ Create an empty audio stream. """
        rw = sdl2.rw_from_object(BytesIO())
        return cls("empty", rw)

    @classmethod
    def from_file(cls, music_file: Path) -> AudioStream:
        """ Create an audio stream from a music file. """
        fp = music_file.open('rb')
        rw = sdl2.rw_from_object(BytesIO(fp.read()))
        return cls(music_file.name, rw, fp)
