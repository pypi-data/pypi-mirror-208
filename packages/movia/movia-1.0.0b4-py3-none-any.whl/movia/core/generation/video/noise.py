#!/usr/bin/env python3

"""
** Generate a video noise signal. **
------------------------------------
"""

from fractions import Fraction
import hashlib
import math
import numbers
import struct
import typing

import torch

from movia.core.classes.container import ContainerInput
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.stream import Stream
from movia.core.classes.stream_video import StreamVideo
from movia.core.exceptions import OutOfTimeRange
from movia.core.interfaces.seedable import Seedable



class GeneratorVideoNoise(ContainerInput, Seedable):
    """
    ** Generate a pure noise video signal. **

    Examples
    --------
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>> stream = GeneratorVideoNoise(0).out_streams[0]
    >>> stream.snapshot(0, (13, 9))[..., 0]
    tensor([[ 11,  17, 169,  48,   9, 217, 124, 113, 195],
            [ 51,  79, 173, 237, 176, 201, 124,  23, 177],
            [167, 187,  49, 153, 107, 249, 128,  89,  51],
            [174,  30, 173,  31, 127, 146, 134,   2, 123],
            [ 19, 151,  41, 219,  95, 199, 138, 180, 188],
            [177, 165,  63,  35, 177, 109, 134, 166, 154],
            [121, 250, 175, 186,   3, 185, 254, 152,   4],
            [193, 215, 220, 140, 151, 230, 148, 159, 213],
            [114, 249, 218, 159, 148, 169, 192, 178, 154],
            [ 80, 145, 195,  94, 102,  14, 190, 252,  45],
            [ 32, 103, 243, 155,  61,   9, 116,  55, 134],
            [255, 154, 249,  56, 146, 217,   0, 102,  48],
            [ 68, 187,  91, 247, 247,  80, 113, 105,  77]], dtype=torch.uint8)
    >>>
    """

    def __init__(self, seed: typing.Optional[numbers.Real]=None):
        """
        Parameters
        ----------
        seed : numbers.Real, optional
            Transmitted to ``movia.core.interfaces.seedable.Seedable``.
        """
        Seedable.__init__(self, seed)
        super().__init__([_StreamVideoNoiseUniform(self)])

    @classmethod
    def default(cls):
        return cls(0)

    def getstate(self) -> dict:
        return self._getstate_seed()

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert set(state) == {"seed"}, set(state)
        self._setstate_seed(state)
        ContainerInput.__init__(self, [_StreamVideoNoiseUniform(self)])


class _StreamVideoNoiseUniform(StreamVideo):
    """
    ** Random video stream where each pixel follows a uniform law. **
    """

    is_space_continuous = True
    is_time_continuous = True

    def __init__(self, node: GeneratorVideoNoise):
        assert isinstance(node, GeneratorVideoNoise), node.__class__.__name__
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, shape: tuple[int, int]) -> FrameVideo:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")
        return FrameVideo(
            timestamp,
            torch.randint(
                0,
                256,
                (*shape, 3),
                generator=torch.random.manual_seed(
                    int.from_bytes(
                        hashlib.md5(
                            struct.pack(
                                "dLL",
                                self.node.seed,
                                timestamp.numerator % (1 << 64),
                                timestamp.denominator % (1 << 64),
                            )
                        ).digest(),
                        byteorder="big",
                    ) % (1 << 64) # solve RuntimeError: Overflow when unpacking long
                ),
                dtype=torch.uint8
            ),
        )

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        return math.inf
