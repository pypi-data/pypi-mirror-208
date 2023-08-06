#!/usr/bin/env python3

"""
** Allows to generate colors from mathematical functions. **
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
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.stream import Stream
from movia.core.classes.stream_video import StreamVideo
from movia.core.compilation.sympy_to_torch import _parse_expr, LambdifyHomogeneous
from movia.core.exceptions import OutOfTimeRange



class GeneratorVideoEquation(ContainerInput):
    """
    ** Generate a video stream whose channels are defened by any equations. **

    Attributes
    ----------
    colors : list[sympy.core.expr.Expr]
        The luminosity expression of the differents channels (readonly).

    Examples
    --------
    >>> from movia.core.generation.video.equation import GeneratorVideoEquation
    >>> (stream,) = GeneratorVideoEquation(
    ...     "atan(pi*j)/pi + 1/2", # dark blue on the left and bright on the right
    ...     "sin(2pi(i-t))**2", # horizontal descending green waves
    ...     "exp(-(i**2+j**2)/(2*(1e-3+.1*t)))", # red spot in the center that grows
    ... ).out_streams
    >>> stream.node.colors
    [atan(pi*j)/pi + 1/2, sin(pi*(2*i - 2*t))**2, exp((-i**2 - j**2)/(0.2*t + 0.002))]
    >>> stream.snapshot(0, (13, 9))[..., 0] # blue at t=0
    tensor([[ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230],
            [ 25,  33,  46,  73, 128, 182, 209, 222, 230]], dtype=torch.uint8)
    >>> stream.snapshot(0, (13, 9))[..., 1] # green at t=0
    tensor([[  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [191, 191, 191, 191, 191, 191, 191, 191, 191],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0]], dtype=torch.uint8)
    >>> stream.snapshot(0, (13, 9))[..., 2] # red at t=0
    tensor([[  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0, 255,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0,   0]], dtype=torch.uint8)
    >>> stream.snapshot(1, (13, 9))[..., 2] # red at t=1
    tensor([[  0,   0,   1,   1,   2,   1,   1,   0,   0],
            [  0,   1,   2,   6,   8,   6,   2,   1,   0],
            [  0,   2,   8,  21,  28,  21,   8,   2,   0],
            [  1,   5,  21,  54,  74,  54,  21,   5,   1],
            [  1,   9,  43, 108, 147, 108,  43,   9,   1],
            [  2,  14,  64, 163, 222, 163,  64,  14,   2],
            [  2,  16,  74, 187, 255, 187,  74,  16,   2],
            [  2,  14,  64, 163, 222, 163,  64,  14,   2],
            [  1,   9,  43, 108, 147, 108,  43,   9,   1],
            [  1,   5,  21,  54,  74,  54,  21,   5,   1],
            [  0,   2,   8,  21,  28,  21,   8,   2,   0],
            [  0,   1,   2,   6,   8,   6,   2,   1,   0],
            [  0,   0,   1,   1,   2,   1,   1,   0,   0]], dtype=torch.uint8)
    >>>
    """

    def __init__(self, *colors: typing.Union[Basic, numbers.Real, str]):
        """
        Parameters
        ----------
        *colors : str or sympy.Basic
            The brightness of the color channels.
            The channels are interpreted like is describe in
            ``movia.core.classes.frame_video.FrameVideo``.
            The return values will be cliped to stay in the range [0, 1].
            The value is 0 for min brightness and 1 for the max.
            If the expression gives a complex, the modiule is taken.
            The variables that can be used in these functions are the following:

                * t : The time in seconds since the beginning of the video.
                * i : The relative position along the vertical axis (numpy convention).
                    This value evolves between -1 and 1.
                * j : The relative position along the horizontal axis (numpy convention).
                    This value evolves between -1 and 1.
        """
        # check
        assert all(isinstance(c, (Basic, numbers.Real, str)) for c in colors), colors
        assert 1 <= len(colors) <= 4, len(colors)

        # cast
        self._colors = [_parse_expr(c) for c in colors]

        # check
        free_symbs = set(map(str, set.union(*(c.free_symbols for c in self._colors))))
        if free_symbs - {"i", "j", "t"}:
            raise ValueError(f"only i, j and t symbols are allowed, not {free_symbs}")

        # delegation
        super().__init__([_StreamVideoEquation(self)])

    @classmethod
    def default(cls):
        return cls(0)

    def getstate(self) -> dict:
        return {"colors": [str(c) for c in self.colors]}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert set(state) == {"colors"}, set(state)
        GeneratorVideoEquation.__init__(self, *state["colors"])

    @property
    def colors(self) -> list[Basic]:
        """
        ** The luminosity expression of the differents channels. **
        """
        return self._colors.copy()


class _StreamVideoEquation(StreamVideo):
    """
    ** Color field parameterized by time and position. **
    """

    is_space_continuous = True
    is_time_continuous = True

    def __init__(self, node: GeneratorVideoEquation):
        assert isinstance(node, GeneratorVideoEquation), node.__class__.__name__
        super().__init__(node)

        # cache
        self._colors_func = None
        self._fields = None

    def _get_colors_func(self) -> callable:
        """
        ** Allows to "compile" equations at the last moment. **
        """
        if self._colors_func is None:
            self._colors_func = LambdifyHomogeneous(
                [Symbol("i"), Symbol("j"), Symbol("t")], self.node.colors
            )
        return self._colors_func

    def _get_fields(self, shape: tuple[int, int]) -> tuple[torch.Tensor, torch.Tensor]:
        """
        ** Returns the i and j field, minimising realloc by cache. **
        """
        height, width = shape
        if self._fields is None or self._fields[0].shape != shape:
            self._fields = torch.meshgrid(
                torch.linspace(-1, 1, height, dtype=torch.float32),
                torch.linspace(-1, 1, width, dtype=torch.float32),
                indexing="ij",
            )
        return self._fields

    def _snapshot(self, timestamp: Fraction, shape: tuple[int, int]) -> FrameVideo:
        # verif
        if timestamp < 0:
            raise OutOfTimeRange(f"there is no video frame at timestamp {timestamp} (need >= 0)")

        # calculation
        i_field, j_field = self._get_fields(shape)
        i_field, j_field = i_field.clone(), j_field.clone()
        colors = self._get_colors_func()(i_field, j_field, float(timestamp))

        # correction + cast
        frame = FrameVideo(
            timestamp,
            torch.empty((*shape, len(self.node.colors)), dtype=torch.uint8),
        )
        for i, col in enumerate(colors):
            if isinstance(col, torch.Tensor):
                if col.dtype.is_complex:
                    col = torch.abs(col)
                torch.nan_to_num(col, nan=127.0/255.0, posinf=1.0, neginf=0.0, out=col)
                torch.clip(col, 0.0, 1.0, out=col)
                col *= 255.0
                torch.round(col, out=col)
                col = col.to(dtype=torch.uint8, copy=False)
            elif isinstance(col, (float, int, complex)):
                if isinstance(col, int):
                    col = float(col)
                elif isinstance(col, complex):
                    col = abs(col)
                if math.isnan(col):
                    col = 127.0/255.0
                col = round(255.0 * max(0.0, min(1.0, col)))
            else:
                raise TypeError(
                    f"{col.__class__.__name__} is not float, int, complex or torch.Tensor"
                )
            frame[:, :, i] = col

        return frame

    @property
    def beginning(self) -> Fraction:
        return Fraction(0)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        return math.inf
