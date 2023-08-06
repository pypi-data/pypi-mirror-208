#!/usr/bin/env python3

"""
** Generate an audio noise signal. **
--------------------------------------
"""

from fractions import Fraction
import itertools
import math
import numbers
import typing

import torch

from movia.core.classes.container import ContainerInput
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudio
from movia.core.exceptions import OutOfTimeRange
from movia.core.interfaces.seedable import Seedable



class GeneratorAudioNoise(ContainerInput, Seedable):
    """
    ** Generate a pure noise audio signal. **

    Examples
    --------
    >>> from fractions import Fraction
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> (stream,) = GeneratorAudioNoise(0).out_streams
    >>> stream.snapshot(Fraction(2, 48000), 48000, 5).numpy(force=True)
    array([[-0.44544228,  0.98969342, -0.94406372, -0.95037923, -0.63161781],
           [-0.84168343, -0.46822516, -0.35403866, -0.92428763, -0.12580545]])
    >>> stream.snapshot(0, 24000, 5).numpy(force=True)
    array([[-0.92382674, -0.44544228, -0.94406372, -0.63161781,  0.499573  ],
           [ 0.52793658, -0.84168343, -0.35403866, -0.12580545,  0.79587791]])
    >>> frame = stream.snapshot(0, 48000, 48000*60) # test uniform
    >>> round(frame.mean().item(), 3) # theory 0
    0.0
    >>> round(frame.var().item(), 3) # theory 1/3
    0.333
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
        super().__init__([_StreamAudioNoiseUniform(self)])

    @classmethod
    def default(cls):
        return cls(0)

    def getstate(self) -> dict:
        return self._getstate_seed()

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert set(state) == {"seed"}, set(state)
        self._setstate_seed(state)
        ContainerInput.__init__(self, [_StreamAudioNoiseUniform(self)])


class _StreamAudioNoiseUniform(StreamAudio):
    """
    ** Random audio stream where each sample follows a uniform law. **

    Based on the md5 hash algorithm on the timestamps.
    """

    is_time_continuous = True

    def __init__(self, node: GeneratorAudioNoise):
        """
        Parameters
        ----------
        node : movia.core.generation.audio.noise.GeneratorAudioNoise
            Simply allows to keep the graph structure.
        """
        assert isinstance(node, GeneratorAudioNoise), node.__class__.__name__
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")
        # initialisation message, depend to the seed and the timestamps
        a_0 = torch.arange(samples, dtype=torch.float64)
        torch.add(torch.multiply(a_0, 1/rate, out=a_0), float(timestamp), out=a_0)
        a_0 = torch.frombuffer(a_0.numpy(force=True), dtype=torch.int32)
        a_0 &= 0b01111111111111111111111111111111 # force >= 0
        b_0 = torch.frombuffer(bytearray(self.node.seed_bytes), dtype=torch.int32)
        b_0 &= 0b01111111111111111111111111111111 # force >= 0
        message = list(itertools.chain(
            b_0.to(dtype=torch.int64).unsqueeze(1),
            a_0.to(dtype=torch.int64).reshape(-1, 2).transpose(0, 1),
            torch.zeros((6, 1), dtype=torch.int64),
        )) # len 16

        # variables declaration
        a_0 = torch.frombuffer(bytearray(b"\x00\x00\x00\x00\x67\x45\x23\x01"), dtype=torch.int64)
        b_0 = torch.frombuffer(bytearray(b"\x00\x00\x00\x00\xef\xcd\xab\x89"), dtype=torch.int64)
        c_0 = torch.frombuffer(bytearray(b"\x00\x00\x00\x00\x98\xba\xdc\xfe"), dtype=torch.int64)
        d_0 = torch.frombuffer(bytearray(b"\x00\x00\x00\x00\x10\x32\x54\x76"), dtype=torch.int64)
        f_0 = torch.empty(1, dtype=torch.int64)

        # compute md5 on each elements
        for i, (const, shift) in enumerate(zip(
            [
                0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
                0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
                0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
                0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
                0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
                0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
                0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
                0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
                0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
                0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
                0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
                0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
                0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
                0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
                0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
                0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
            ],
            [
                7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
                5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
                4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
                6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,
            ],
        )):
            if i <= 15:
                # f_0 = (b_0 & c_0) ^ ((~b_0) & a_0)
                # f_0 = torch.bitwise_xor(d_0, torch.bitwise_and(b_0, torch.bitwise_xor(c_0, d_0)))
                f_0 = torch.bitwise_xor(
                    c_0, d_0, out=(f_0 if len(f_0) == max(len(c_0), len(d_0)) else None)
                )
                f_0 = torch.bitwise_and(b_0, f_0, out=(f_0 if len(f_0) == len(b_0) else None))
                f_0 = torch.bitwise_xor(d_0, f_0, out=(f_0 if len(f_0) == len(d_0) else None))
                g_0 = i
            elif i <= 31:
                # f_0 = (d_0 & b_0) ^ ((~d_0) & c_0)
                # f_0 = torch.bitwise_xor(c_0, torch.bitwise_and(d_0, torch.bitwise_xor(b_0, c_0)))
                f_0 = torch.bitwise_xor(
                    b_0, c_0, out=(f_0 if len(f_0) == max(len(b_0), len(c_0)) else None)
                )
                f_0 = torch.bitwise_and(d_0, f_0, out=(f_0 if len(f_0) == len(d_0) else None))
                f_0 = torch.bitwise_xor(c_0, f_0, out=(f_0 if len(f_0) == len(c_0) else None))
                g_0 = (5*i + 1) % 16
            elif i <= 47:
                # f_0 = torch.bitwise_xor(torch.bitwise_xor(b_0, c_0), d_0)
                f_0 = torch.bitwise_xor(
                    b_0, c_0, out=(f_0 if len(f_0) == max(len(b_0), len(c_0)) else None)
                )
                f_0 = torch.bitwise_xor(f_0, d_0, out=(f_0 if len(f_0) == len(d_0) else None))
                g_0 = (3*i + 5) % 16
            else:
                # f_0 = torch.bitwise_xor(c_0, b_0 ^ (~d_0))
                f_0 = ~d_0 # bug when try inplace
                f_0 = torch.bitwise_or(b_0, f_0, out=(f_0 if len(f_0) == len(b_0) else None))
                f_0 = torch.bitwise_xor(c_0, f_0, out=(f_0 if len(f_0) == len(c_0) else None))
                g_0 = (7*i) % 16

            f_0 += const
            f_0 = torch.add(f_0, a_0, out=(f_0 if len(f_0) == len(a_0) else None))
            f_0 = f_0 + message[g_0] # bug when try inplace

            f_0 <<= shift
            f_0 ^= f_0 >> 32
            f_0 &= 0x00000000ffffffff # mod 2**32
            a_0, b_0, c_0, d_0 = d_0, f_0, b_0, c_0
        del message

        # concat elements and convertion to float64 range 0 1 uniform
        a_0 ^= b_0 << 32
        c_0 ^= d_0 << 32
        del b_0, d_0
        a_0 &= 0b0_00000000000_1111111111111111111111111111111111111111111111111111
        c_0 &= 0b0_00000000000_1111111111111111111111111111111111111111111111111111
        a_0 ^= 0b0_01111111111_0000000000000000000000000000000000000000000000000000
        c_0 ^= 0b0_01111111111_0000000000000000000000000000000000000000000000000000
        a_0, c_0 = (
            torch.frombuffer(a_0.numpy(force=True), dtype=torch.float64), # brut cast in float64
            torch.frombuffer(c_0.numpy(force=True), dtype=torch.float64), # brut cast in float64
        )

        # cast to StreamAudio
        return FrameAudio(
            timestamp,
            rate,
            torch.vstack(
                [
                    torch.mul(torch.add(a_0, -1.5, out=a_0), 2, out=a_0), # [1, 2[ -> [-1, 1[
                    torch.mul(torch.add(c_0, -1.5, out=c_0), 2, out=c_0), # [1, 2[ -> [-1, 1[
                ]
            )
        )

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def channels(self) -> int:
        return 2

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        return math.inf
