import sdl2.sdlmixer

from potion.content import Content


class Music:
    """ A long form music file. """
    def __init__(self, content_path: str) -> None:
        """ `content_path` is the path to the audio file. """
        self._name = content_path
        self._audio_stream = Content.load_audio_stream(content_path)

    def __str__(self) -> str:
        return f"Music({self._name})"

    def __repr__(self) -> str:
        return str(self)

    def play(self, loops: int = -1) -> None:
        """ Play the music.

        If loops is -1, it will play infinitely.
        """
        sdl2.sdlmixer.Mix_PlayMusic(music=self._audio_stream.sdl_mix_music, loops=loops)

    @classmethod
    def pause(cls) -> None:
        """ Pause the music """
        sdl2.sdlmixer.Mix_PauseMusic()

    @classmethod
    def resume(cls) -> None:
        """ Resume the music. """
        sdl2.sdlmixer.Mix_ResumeMusic()

    @classmethod
    def stop(cls) -> None:
        """ Stop the music. """
        sdl2.sdlmixer.Mix_HaltMusic()

    @classmethod
    def rewind(cls) -> None:
        """ Rewind the music. """
        sdl2.sdlmixer.Mix_RewindMusic()

    @classmethod
    def fade_out(cls, fade_time_ms: int) -> None:
        """ Fade the music out over a number of milliseconds, and then stop. """
        sdl2.sdlmixer.Mix_FadeOutMusic(fade_time_ms)

    def fade_in(self, fade_time_ms: int, loops: int = -1) -> None:
        """ Fade the music in over a number of milliseconds. """
        sdl2.sdlmixer.Mix_FadeInMusic(music=self._audio_stream.sdl_mix_music, loops=loops, ms=fade_time_ms)
