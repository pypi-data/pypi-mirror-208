#!/usr/bin/env python3

"""
** Allows to generate sound from mathematical functions. **
------------------------------------------------------------
"""

from fractions import Fraction
import math
import numbers
import typing

from sympy.core.basic import Basic
from sympy.core.symbol import Symbol
import torch

from movia.core.classes.container import ContainerInput
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudio
from movia.core.compilation.sympy_to_torch import _parse_expr, LambdifyHomogeneous
from movia.core.exceptions import OutOfTimeRange



class GeneratorAudioEquation(ContainerInput):
    """
    ** Generate an audio stream whose channels are defened by any equations. **

    Attributes
    ----------
    signals : list[sympy.core.expr.Expr]
        The amplitude expression of the differents channels (readonly).

    Examples
    --------
    >>> import torch
    >>> from movia.core.generation.audio.equation import GeneratorAudioEquation
    >>> (stream,) = GeneratorAudioEquation("sin(2*pi*440*t)").out_streams
    >>> torch.round(stream.snapshot(0, 3520, 8), decimals=3)
    FrameAudio(Fraction(0, 1), 3520, [[ 0.     0.707  1.     0.707  0.    -0.707 -1.    -0.707]])
    >>>
    """

    def __init__(self, *signals: typing.Union[Basic, numbers.Real, str]):
        """
        Parameters
        ----------
        *signals : str or sympy.Basic
            The amplitude function of each channel respectively.
            The number of expressions correspond to the number of channels.
            The return values will be cliped to stay in the range [-1, 1].
            If the expression gives a complex, the real part is taken.
            The variable `t` fits the time in seconds since the beginning of the audio.
        """
        # check
        assert all(isinstance(s, (Basic, numbers.Real, str)) for s in signals), signals
        assert len(signals) >= 1, "a minimum of one signal is require"

        # cast
        self._signals = [_parse_expr(s) for s in signals]

        # check
        free_symbs = set(map(str, set.union(*(s.free_symbols for s in self._signals))))
        if free_symbs - {"t"}:
            raise ValueError(f"only t symbols is allowed, not {free_symbs}")

        # delegation
        super().__init__([_StreamAudioEquation(self)])

    @classmethod
    def default(cls):
        return cls(0)

    def getstate(self) -> dict:
        return {
            "signals": [str(s) for s in self.signals],
        }

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert set(state) == {"signals"}, set(state)
        GeneratorAudioEquation.__init__(self, *state["signals"])

    @property
    def signals(self) -> list[Basic]:
        """
        ** The amplitude expression of the differents channels. **
        """
        return self._signals.copy()


class _StreamAudioEquation(StreamAudio):
    """
    ** Channels field parameterized by time. **
    """

    is_time_continuous = True

    def __init__(self, node: GeneratorAudioEquation):
        assert isinstance(node, GeneratorAudioEquation), node.__class__.__name__
        super().__init__(node)

        # compilation
        self._signals_func = None

    def _get_signals_func(self) -> callable:
        """
        ** Allows to "compile" equations at the last moment. **
        """
        if self._signals_func is None:
            self._signals_func = LambdifyHomogeneous(
                [Symbol("t")], self.node.signals
            )
        return self._signals_func

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        # verif
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no audio frame at timestamp {timestamp} (need >= 0)")
        time_field = torch.arange(samples, dtype=int) # not float directely for avoid round mistakes
        time_field = time_field.to(dtype=torch.float64, copy=False)
        time_field /= float(rate)
        time_field += float(timestamp)
        frame = FrameAudio(
            timestamp, rate, torch.empty((self.channels, samples), dtype=torch.float32)
        )
        samples = self._get_signals_func()(time_field)
        for i, samples_ in enumerate(samples):
            if isinstance(samples_, torch.Tensor):
                if samples_.dtype.is_complex:
                    samples_ = torch.real(samples_)
                torch.nan_to_num(samples_, nan=0.0, posinf=1.0, neginf=-1.0, out=samples_)
                torch.clip(samples_, -1.0, 1.0, out=samples_)
            elif isinstance(samples_, (float, int, complex)):
                if isinstance(samples_, int):
                    samples_ = float(samples_)
                elif isinstance(samples_, complex):
                    samples_ = samples_.real
                if math.isnan(samples_):
                    samples_ = 0.0
                samples_ = max(-1.0, min(1.0, samples_))
            else:
                raise TypeError(
                    f"{samples.__class__.__name__} is not float, int, complex or torch.Tensor"
                )

            frame[i, :] = samples_
        return frame

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def channels(self) -> int:
        return len(self.node.signals)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        return math.inf
