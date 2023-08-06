#!/usr/bin/env python3

"""
** Split a stream in several slices. **
---------------------------------------
"""

from fractions import Fraction
import math
import numbers
import typing

from movia.core.classes.filter import Filter
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudioWrapper
from movia.core.classes.stream_video import StreamVideoWrapper
from movia.core.exceptions import OutOfTimeRange



class FilterCut(Filter):
    """
    ** Splits the stream at the given positions. **

    Attributes
    ----------
    limits : list[Fraction]
        The ordered limits of each slices in seconds (readonly).

    Examples
    --------
    >>> from movia.core.exceptions import OutOfTimeRange
    >>> from movia.core.filters.basic.cut import FilterCut
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> a_0, v_0, a_1, v_1, a_2, v_2 = FilterCut([s_base_audio, s_base_video], 10, 20).out_streams
    >>>
    >>> a_0.beginning, a_0.duration
    (Fraction(0, 1), Fraction(10, 1))
    >>> _ = a_0.snapshot(0, 1, 1) # [0, 1[
    >>> _ = a_0.snapshot(9, 1, 1) # [9, 10[
    >>> try:
    ...     _ = a_0.snapshot(9, 1, 2) # [9, 11[
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 0 and over 10 seconds, eval from 9 to length 2/1
    >>> a_1.beginning, a_1.duration
    (Fraction(10, 1), Fraction(10, 1))
    >>> _ = a_1.snapshot(10, 1, 1) # [10, 11[
    >>> _ = a_1.snapshot(19, 1, 1) # [19, 20[
    >>> try:
    ...     _ = a_1.snapshot(19, 1, 2) # [19, 21[
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 10 and over 20 seconds, eval from 19 to length 2/1
    >>> try:
    ...     _ = a_1.snapshot(9, 1, 2) # [9, 11[
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 10 and over 20 seconds, eval from 9 to length 2/1
    >>> a_2.beginning, a_2.duration
    (Fraction(20, 1), inf)
    >>> _ = a_2.snapshot(20, 1, 1) # [20, 21[
    >>> try:
    ...     _ = a_2.snapshot(19, 1, 2) # [19, 21[
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 20 and over inf seconds, eval from 19 to length 2/1
    >>>
    >>> v_0.beginning, v_0.duration
    (Fraction(0, 1), Fraction(10, 1))
    >>> _ = v_0.snapshot(0, (1, 1))
    >>> _ = v_0.snapshot(9, (1, 1))
    >>> try:
    ...     _ = v_0.snapshot(10, (1, 1))
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 0 and over 10 seconds, evaluation at 10 seconds
    >>> v_1.beginning, v_1.duration
    (Fraction(10, 1), Fraction(10, 1))
    >>> _ = v_1.snapshot(10, (1, 1))
    >>> _ = v_1.snapshot(19, (1, 1))
    >>> try:
    ...     _ = v_1.snapshot(9, (1, 1))
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 10 and over 20 seconds, evaluation at 9 seconds
    >>> try:
    ...     _ = v_1.snapshot(20, (1, 1))
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 10 and over 20 seconds, evaluation at 20 seconds
    >>> v_2.beginning, v_2.duration
    (Fraction(20, 1), inf)
    >>> try:
    ...     _ = v_2.snapshot(19, (1, 1))
    ... except OutOfTimeRange as err:
    ...     print(err)
    ...
    the stream has been truncated under 20 and over inf seconds, evaluation at 19 seconds
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream], *limits: numbers.Real):
        """
        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``movia.core.filters.basic.cut.FilterCut``.
        limits : numbers.Real
            The temporal limits between the differents slices.
            The timings are like a duration relative to the beginning of the first stream.
        """
        assert hasattr(in_streams, "__iter__"), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert all(isinstance(stream, Stream) for stream in in_streams), \
            [stream.__class__.__name__ for stream in in_streams]
        assert all(isinstance(l, numbers.Real) for l in limits), limits
        assert all(map(math.isfinite, limits)), limits
        assert all(l >= 0 for l in limits), min(limits)

        self._limits = list(map(Fraction, limits))
        assert sorted(self._limits) == self._limits, f"limits are not sorted, {limits}"
        assert len(set(self._limits)) == len(self._limits), f"some limits are equal, {limits}"

        super().__init__(in_streams, in_streams)
        if not self.in_streams:
            return

        beginning = min(s.beginning for s in self.in_streams)
        abs_limits = [l + beginning for l in self._limits]
        abs_limits_min = [-math.inf] + abs_limits
        abs_limits_max = abs_limits + [math.inf]
        super().__init__(
            self.in_streams, # not in_stream without self because generator can be exausted
            [
                (
                    {"audio": _StreamAudioCut, "video": _StreamVideoCut}
                )[in_stream.type](self, index, l_min, l_max)
                for l_min, l_max in zip(abs_limits_min, abs_limits_max)
                for index, in_stream in enumerate(self.in_streams)
            ]
        )

    @classmethod
    def default(cls):
        return cls([])

    def getstate(self) -> dict:
        return {"limits": list(map(str, self.limits))}

    @property
    def limits(self):
        """
        ** The ordered limits of each slices in seconds. **
        """
        return self._limits.copy()

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert set(state) == {"limits"}, set(state)
        limits = map(Fraction, state["limits"])
        FilterCut.__init__(self, in_streams, *limits)


class _StreamAudioCut(StreamAudioWrapper):
    """
    ** Select a slice of an audio stream. **
    """

    def __init__(self,
        node: FilterCut, index: numbers.Integral, l_min: numbers.Real, l_max: numbers.Real
    ):
        """
        Parameters
        ----------
        filter : movia.core.classes.filter.Filter
            Transmitted to ``movia.core.classes.stream_audio.StreamAudioWrapper``.
        index : numbers.Integral
            Transmitted to ``movia.core.classes.stream_audio.StreamAudioWrapper``.
        l_min : numbers.Real
            The low absolute limit.
        l_max : numbers.Real
            The high absolute limit.
        """
        assert isinstance(node, FilterCut), node.__class__.__name__
        assert isinstance(l_min, numbers.Real), l_min.__class__.__name__
        assert isinstance(l_max, numbers.Real), l_max.__class__.__name__
        super().__init__(node, index)
        self.l_min, self.l_max = l_min, l_max

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        if timestamp + Fraction(samples, rate) > self.l_max or timestamp < self.l_min:
            raise OutOfTimeRange(
                "the stream has been truncated under "
                f"{self.beginning} and over {self.beginning+self.duration} seconds, "
                f"eval from {timestamp} to length {samples}/{rate}"
            )
        return self.stream._snapshot(timestamp, rate, samples)

    @property
    def beginning(self) -> Fraction:
        return max(min(self.l_min, self.l_max), self.stream.beginning)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        end = min(max(self.l_min, self.l_max), self.stream.beginning+self.stream.duration)
        return end - self.beginning


class _StreamVideoCut(StreamVideoWrapper):
    """
    ** Select a slice of a video stream. **
    """

    def __init__(self,
        node: FilterCut, index: numbers.Integral, l_min: numbers.Real, l_max: numbers.Real
    ):
        """
        Parameters
        ----------
        filter : movia.core.filters.basic.cut.FilterCut
            Transmitted to ``movia.core.classes.stream_video.StreamVideoWrapper``.
        index : numbers.Integral
            Transmitted to ``movia.core.classes.stream_video.StreamVideoWrapper``.
        l_min : numbers.Real
            The low absolute limit.
        l_max : numbers.Real
            The high absolute limit.
        """
        assert isinstance(node, FilterCut), node.__class__.__name__
        assert isinstance(l_min, numbers.Real), l_min.__class__.__name__
        assert isinstance(l_max, numbers.Real), l_max.__class__.__name__
        super().__init__(node, index)
        self.l_min, self.l_max = l_min, l_max

    def _snapshot(self, timestamp: Fraction, shape: tuple[int, int]) -> FrameVideo:
        if timestamp >= self.l_max or timestamp < self.l_min:
            raise OutOfTimeRange(
                f"the stream has been truncated under "
                f"{self.beginning} and over {self.beginning+self.duration} seconds, "
                f"evaluation at {timestamp} seconds"
            )
        return self.stream._snapshot(timestamp, shape)

    @property
    def beginning(self) -> Fraction:
        return max(min(self.l_min, self.l_max), self.stream.beginning)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        end = min(max(self.l_min, self.l_max), self.stream.beginning+self.stream.duration)
        return end - self.beginning
