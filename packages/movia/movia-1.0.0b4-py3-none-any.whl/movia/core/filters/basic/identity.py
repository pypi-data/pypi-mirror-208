#!/usr/bin/env python3

"""
** A filter that doing nothing. **
----------------------------------
"""

import typing

from movia.core.classes.filter import Filter
from movia.core.classes.stream import Stream


class FilterIdentity(Filter):
    """
    ** Allows to convert a set of streams into a filter. **

    Examples
    --------
    >>> from movia.core.filters.basic.identity import FilterIdentity
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> identity = FilterIdentity([s_base_audio, s_base_video])
    >>>
    >>> s_base_audio is identity.out_streams[0]
    True
    >>> s_base_video is identity.out_streams[1]
    True
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream]):
        """
        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            All the streams to keep intact.
            Transmitted to ``movia.core.filters.basic.cut.FilterCut``.
        """
        super().__init__(in_streams, in_streams)

    @classmethod
    def default(cls):
        return cls([])

    def getstate(self) -> dict:
        return {}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterIdentity.__init__(self, in_streams)
