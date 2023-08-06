#!/usr/bin/env python3

"""
** Dedicated to tests, it is an empty audio stream containing no samples. **
----------------------------------------------------------------------------
"""

from fractions import Fraction
import typing

from movia.core.classes.container import ContainerInput
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudio
from movia.core.exceptions import OutOfTimeRange



class GeneratorAudioEmpty(ContainerInput):
    """
    ** Contains an empty audio stream. **

    Examples
    --------
    >>> from movia.core.exceptions import OutOfTimeRange
    >>> from movia.core.generation.audio.empty import GeneratorAudioEmpty
    >>> (stream,) = GeneratorAudioEmpty().out_streams
    >>> try:
    ...     stream.snapshot(0)
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    this stream does not contain any samples
    >>>
    """

    def __init__(self):
        out_streams = [_StreamAudioEmpty(self)]
        super().__init__(out_streams)

    @classmethod
    def default(cls):
        return cls()

    def getstate(self) -> dict:
        return {}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}, state
        GeneratorAudioEmpty.__init__(self)


class _StreamAudioEmpty(StreamAudio):
    """
    ** An audio stream containing no sample. **
    """

    is_time_continuous = True

    def __init__(self, node: GeneratorAudioEmpty):
        assert isinstance(node, GeneratorAudioEmpty), node.__class__.__name__
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        raise OutOfTimeRange("this stream does not contain any samples")

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def channels(self) -> int:
        raise KeyError("it makes no sense to give a number of channels to an absence of sample")

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        return Fraction(0)
