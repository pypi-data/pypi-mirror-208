#!/usr/bin/env python3

"""
** Allows you to temporarily translate a sequence. **
-----------------------------------------------------
"""

from fractions import Fraction
import numbers
import typing

from movia.core.classes.filter import Filter
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudioWrapper
from movia.core.classes.stream_video import StreamVideoWrapper



class FilterTranslate(Filter):
    """
    ** Change the beginning time of a stream. **

    Attributes
    ----------
    delay : Fraction
        The delay append to the original beginning time of the stream (readonly).
        a positive value indicates that the output flow is later than the input flow.

    Examples
    --------
    >>> from movia.core.filters.basic.translate import FilterTranslate
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_base_audio,) = GeneratorAudioNoise(0).out_streams
    >>> (s_base_video,) = GeneratorVideoNoise(0).out_streams
    >>> s_trans_audio, s_trans_video = FilterTranslate([s_base_audio, s_base_video], 10).out_streams
    >>>
    >>> (s_base_audio.snapshot(0) == s_trans_audio.snapshot(10)).all()
    tensor(True)
    >>> (s_base_video.snapshot(0, (1, 1)) == s_trans_video.snapshot(10, (1, 1))).all()
    tensor(True)
    >>> (s_base_audio.snapshot(10) == s_trans_audio.snapshot(10)).all()
    tensor(False)
    >>> (s_base_video.snapshot(10, (1, 1)) == s_trans_video.snapshot(10, (1, 1))).all()
    tensor(False)
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream], delay: numbers.Real):
        """
        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``movia.core.classes.filter.Filter``.
        delay : numbers.Real
            The temporal translation value to apply at the output stream.
        """
        assert hasattr(in_streams, "__iter__"), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert all(isinstance(stream, Stream) for stream in in_streams), \
            [stream.__class__.__name__ for stream in in_streams]
        assert isinstance(delay, numbers.Real), delay.__class__.__name__

        self._delay = Fraction(delay)
        super().__init__(in_streams, in_streams)
        super().__init__(
            self.in_streams, # not in_stream without self because generator can be exausted
            [
                (
                    {"audio": _StreamAudioTranslate, "video": _StreamVideoTranslate}
                )[in_stream.type](self, index) for index, in_stream in enumerate(self.in_streams)
            ]
        )

    @classmethod
    def default(cls):
        return cls([], 0)

    @property
    def delay(self) -> Fraction:
        """
        ** The delay append to the original beginning time of the stream. **
        """
        return self._delay

    def getstate(self) -> dict:
        return {"delay": str(self.delay)}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert set(state) == {"delay"}, set(state)
        FilterTranslate.__init__(self, in_streams, Fraction(state["delay"]))


class _StreamAudioTranslate(StreamAudioWrapper):
    """
    ** Translate an audio stream from a certain delay. **
    """

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        frame = self.stream._snapshot(timestamp - self.node.delay, rate, samples)
        frame = FrameAudio(frame.time + self.node.delay, rate, frame)
        return frame

    @property
    def beginning(self) -> Fraction:
        return self.stream.beginning + self.node.delay


class _StreamVideoTranslate(StreamVideoWrapper):
    """
    ** Translate a video stream from a certain delay. **
    """

    def _snapshot(self, timestamp: Fraction, shape: tuple[int, int]) -> FrameVideo:
        frame = self.stream._snapshot(timestamp - self.node.delay, shape)
        frame = FrameVideo(frame.time + self.node.delay, frame)
        return frame

    @property
    def beginning(self) -> Fraction:
        return self.stream.beginning + self.node.delay
