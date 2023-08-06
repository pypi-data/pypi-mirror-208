#!/usr/bin/env python3

"""
** Dedicated to tests, it is an empty video stream containing no frames. **
---------------------------------------------------------------------------
"""

from fractions import Fraction
import typing

from movia.core.classes.container import ContainerInput
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.stream import Stream
from movia.core.classes.stream_video import StreamVideo
from movia.core.exceptions import OutOfTimeRange



class GeneratorVideoEmpty(ContainerInput):
    """
    ** Contains an empty video stream. **

    Examples
    --------
    >>> from movia.core.exceptions import OutOfTimeRange
    >>> from movia.core.generation.video.empty import GeneratorVideoEmpty
    >>> (stream,) = GeneratorVideoEmpty().out_streams
    >>> try:
    ...     stream.snapshot(0, (1, 1))
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    this stream does not contain any frames
    >>>
    """

    def __init__(self):
        out_streams = [_StreamVideoEmpty(self)]
        super().__init__(out_streams)

    @classmethod
    def default(cls):
        return cls()

    def getstate(self) -> dict:
        return {}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}, state
        GeneratorVideoEmpty.__init__(self)


class _StreamVideoEmpty(StreamVideo):
    """
    ** A video stream containing no frames. **
    """

    is_space_continuous = False
    is_time_continuous = False

    def __init__(self, node: GeneratorVideoEmpty):
        assert isinstance(node, GeneratorVideoEmpty), node.__class__.__name__
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, shape: tuple[int, int]) -> FrameVideo:
        raise OutOfTimeRange("this stream does not contain any frames")

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        return Fraction(0)
