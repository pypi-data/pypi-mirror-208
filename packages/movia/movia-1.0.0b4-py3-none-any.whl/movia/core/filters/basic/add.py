#!/usr/bin/env python3

"""
** Allows you to combine overlapping streams. **
------------------------------------------------
"""

from fractions import Fraction
import math
import typing

import numpy as np
import torch

from movia.core.classes.filter import Filter
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.node import Node
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudio
from movia.core.classes.stream_video import StreamVideo
from movia.core.exceptions import OutOfTimeRange



class FilterAdd(Filter):
    """
    ** Combine the stream in once by additing the overlapping slices. **

    Examples
    --------
    >>> from movia.core.filters.basic.add import FilterAdd
    >>> from movia.core.filters.basic.translate import FilterTranslate
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.generation.video.equation import GeneratorVideoEquation
    >>>
    >>> (s_audio_0,) = GeneratorAudioNoise(0).out_streams
    >>> (s_audio_1,) = FilterTranslate(GeneratorAudioNoise(.5).out_streams, 10).out_streams
    >>> (s_add_audio,) = FilterAdd([s_audio_0, s_audio_1]).out_streams
    >>> (s_video_0,) = GeneratorVideoEquation("i", "1/2").out_streams
    >>> (s_video_1,) = FilterTranslate(
    ...     GeneratorVideoEquation("j", "1/2").out_streams, 10
    ... ).out_streams
    >>> (s_add_video,) = FilterAdd([s_video_0, s_video_1]).out_streams
    >>>
    >>> s_audio_0.snapshot(8, 1, 5)
    FrameAudio(Fraction(8, 1), 1, [[ 0.51332252  0.6962532  -0.3611679  -0.62504067  0.82771811]
                                   [ 0.22561401 -0.41682793  0.53702945  0.27432338  0.54749512]],
                                  dtype=torch.float64)
    >>> s_audio_1.snapshot(10, 1, 3)
    FrameAudio(Fraction(10, 1), 1, [[-0.48753882  0.45331555 -0.94927975]
                                    [-0.64931847 -0.13948568  0.4026663 ]],
                                   dtype=torch.float64)
    >>> s_add_audio.snapshot(8, 1, 5)
    FrameAudio(Fraction(8, 1), 1, [[ 0.51332252  0.6962532  -0.84870671 -0.17172512 -0.12156164]
                                   [ 0.22561401 -0.41682793 -0.11228902  0.1348377   0.95016141]],
                                  dtype=torch.float64)
    >>>
    >>> s_video_0.snapshot(10, (2, 2))
    FrameVideo(Fraction(10, 1), [[[  0 128]
                                  [  0 128]]
    <BLANKLINE>
                                 [[255 128]
                                  [255 128]]])
    >>> s_video_1.snapshot(10, (2, 2))
    FrameVideo(Fraction(10, 1), [[[  0 128]
                                  [255 128]]
    <BLANKLINE>
                                 [[  0 128]
                                  [255 128]]])
    >>> s_add_video.snapshot(10, (2, 2))
    FrameVideo(Fraction(10, 1), [[[  0 191]
                                  [ 84 191]]
    <BLANKLINE>
                                 [[170 191]
                                  [255 191]]])
    >>>
    """

    def __init__(self, in_streams: typing.Iterable[Stream]):
        """
        Parameters
        ----------
        in_streams : typing.Iterable[Stream]
            Transmitted to ``movia.core.classes.filter.Filter``.
            About the overlaping portions, if the stream is an audio stream,
            a simple addition is performed but if the stream is a video stream,
            the frames are combined like a superposition of semi-transparent windows.
        """
        super().__init__(in_streams, in_streams)
        if not self.in_streams:
            return
        kind = {s.type for s in self.in_streams}
        assert len(kind) == 1, f"impossible to add different type of streams {kind}"
        kind = kind.pop()
        if kind == "audio":
            super().__init__(self.in_streams, [_StreamAudioAdd(self)])
        elif kind == "video":
            super().__init__(self.in_streams, [_StreamVideoAdd(self)])
        else:
            raise NotImplementedError(f"not yet supported {kind}")

    @classmethod
    def default(cls):
        return cls([])

    def getstate(self) -> dict:
        return {}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterAdd.__init__(self, in_streams)


class _StreamVideoAdd(StreamVideo):
    """
    ** Concatenate and mix the video streams. **
    """

    def __init__(self, node: Node):
        """
        Parameters
        ----------
        node : movia.core.filters.basic.add.FilterAdd
            The node containing the StreamVideo to mix.
        """
        assert isinstance(node, FilterAdd), node.__class__.__name__
        assert node.in_streams, "requires at least 1 video stream to add"
        super().__init__(node)

    @staticmethod
    def _add_2_with_1(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Add a gray frame to the gray alpha frame_ref. **

        No verifications are performed for performance reason.
        Not inplace, `ref` and `other` are not changed.

        alpha final = 255
        color final = (c_r*a_r + c_o*(255-a_r))/255

        Examples
        --------
        >>> import torch
        >>> from movia.core.classes.frame_video import FrameVideo
        >>> from movia.core.filters.basic.add import _StreamVideoAdd
        >>> ref = FrameVideo(0, 3, 3, 2) # 3x3 gray alpha
        >>> ref[..., 1] = torch.tensor([0, 127, 255]) # set alpha transparent to blind
        >>> ref[..., 1]
        tensor([[  0, 127, 255],
                [  0, 127, 255],
                [  0, 127, 255]], dtype=torch.uint8)
        >>> ref[..., 0] = torch.tensor([[0], [127], [255]]) # set different gray scale
        >>> ref[..., 0]
        tensor([[  0,   0,   0],
                [127, 127, 127],
                [255, 255, 255]], dtype=torch.uint8)
        >>> other_black = torch.full((3, 3, 1), 0, dtype=torch.uint8)
        >>> other_gray = torch.full((3, 3, 1), 127, dtype=torch.uint8)
        >>> other_white = torch.full((3, 3, 1), 255, dtype=torch.uint8)
        >>>
        >>> _StreamVideoAdd._add_2_with_1(ref, other_black)[..., 0]
        tensor([[  0,   0,   0],
                [  0,  63, 127],
                [  0, 127, 255]], dtype=torch.uint8)
        >>> _StreamVideoAdd._add_2_with_1(ref, other_gray)[..., 0]
        tensor([[127,  63,   0],
                [127, 127, 127],
                [127, 190, 255]], dtype=torch.uint8)
        >>> _StreamVideoAdd._add_2_with_1(ref, other_white)[..., 0]
        tensor([[255, 128,   0],
                [255, 191, 127],
                [255, 255, 255]], dtype=torch.uint8)
        >>>
        """
        a_r = ref[..., 1].to(dtype=torch.float16) # a_r
        a_r /= 255.0 # a_r/255
        color = ref[..., 0].to(dtype=torch.float16) # c_r
        c_o = other[..., 0].to(dtype=torch.float16) # c_o
        color -= c_o # c_r - c_o
        color *= a_r # a_r/255 * (c_r-c_o)
        color += c_o # a_r/255 * (c_r - c_o) + c_o = (c_r*a_r + c_o*(255-a_r))/255
        color = torch.unsqueeze(color.to(dtype=torch.uint8), 2) # shape (height, width, 1)
        return FrameVideo(ref.time, color)

    @staticmethod
    def _add_2_with_2(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Add a gray alpha frame to the gray alpha frame_ref. **

        No verifications are performed for performance reason.
        ``other`` remains unchanged but ``ref`` is changed inplace.
        Returns a pointer of ``ref``.

        alpha final = 255 - ((255-a_r)*(255-a_o))/255
        color final = (c_r*a_r/255 + c_o*a_o/255*(255-a_r)/255) / (a_r/255+a_o/255-a_r/255*a_o/255)

        Examples
        --------
        >>> import torch
        >>> from movia.core.classes.frame_video import FrameVideo
        >>> from movia.core.filters.basic.add import _StreamVideoAdd
        >>> ref = FrameVideo(0, 3, 3, 2) # 3x3 gray alpha
        >>> ref[..., 1] = torch.tensor([0, 127, 255]) # set alpha transparent to blind
        >>> ref[..., 1] # a_r
        tensor([[  0, 127, 255],
                [  0, 127, 255],
                [  0, 127, 255]], dtype=torch.uint8)
        >>> ref[..., 0] = torch.tensor([[0], [127], [255]]) # set different gray scale
        >>> ref[..., 0] # c_r and a_o
        tensor([[  0,   0,   0],
                [127, 127, 127],
                [255, 255, 255]], dtype=torch.uint8)
        >>> other_black = torch.full((3, 3, 2), 0, dtype=torch.uint8)
        >>> other_black[..., 1] = torch.tensor([[0], [127], [255]]) # set alpha transparent to blind
        >>> other_gray = torch.full((3, 3, 2), 127, dtype=torch.uint8)
        >>> other_gray[..., 1] = torch.tensor([[0], [127], [255]])
        >>> other_white = torch.full((3, 3, 2), 255, dtype=torch.uint8)
        >>> other_white[..., 1] = torch.tensor([[0], [127], [255]])
        >>>
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_black)[..., 1] # alpha
        tensor([[  0, 127, 255],
                [127, 190, 255],
                [255, 255, 255]], dtype=torch.uint8)
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_black)[..., 0] # doctest: +ELLIPSIS
        tensor([[...,   0,   0],
                [  0,  84, 127],
                [  0, 127, 255]], dtype=torch.uint8)
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_gray)[..., 0] # doctest: +ELLIPSIS
        tensor([[...,   0,   0],
                [127, 127, 127],
                [127, 190, 255]], dtype=torch.uint8)
        >>> _StreamVideoAdd._add_2_with_2(ref.clone(), other_white)[..., 0] # doctest: +ELLIPSIS
        tensor([[...,   0,   0],
                [255, 169, 127],
                [255, 255, 255]], dtype=torch.uint8)
        >>>
        """
        a_r = ref[..., 1].to(dtype=torch.float16) # a_r
        a_r /= 255.0 # a_r/255
        a_o = other[..., 1].to(dtype=torch.float16) # a_r
        a_o /= 255.0 # a_r/255
        c_r = ref[..., 0].to(dtype=torch.float16) # c_r
        c_o = other[..., 0].to(dtype=torch.float16) # c_r

        alpha = a_r * a_o # a_r/255*a_o/255
        alpha = torch.neg(alpha, out=alpha) # -a_r/255*a_o/255
        alpha += a_o # a_o/255 - a_r/255*a_o/255 = a_o/255 * (255-a_r)/255
        color = c_o * alpha # c_o * a_o/255 * (255-a_r)/255
        color += c_r * a_r # (c_r * a_r/255) + (c_o * a_o/255 * (255-a_r)/255)
        alpha += a_r # a_r/255 + a_o/255 - a_r/255*a_o/255
        color /= alpha # (c_r*a_r/255+c_o*a_o/255*(255-a_r)/255) / (a_r/255+a_o/255-a_r/255*a_o/255)
        alpha *= 255.0 # 255*(a_r/255 + a_o/255 - a_r/255*a_o/255) = 255 - ((255-a_r)*(255-a_o))/255

        ref[..., 0] = color # cast automatic
        ref[..., 1] = alpha # cast automatic
        return ref

    @staticmethod
    def _add_2_with_3(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Pseudo alias to ``from movia.core.filters.basic.add._StreamVideoAdd._add_4_with_3``. **
        """
        return _StreamVideoAdd._add_4_with_3(ref.convert(4), other)

    @staticmethod
    def _add_2_with_4(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Pseudo alias to ``from movia.core.filters.basic.add._StreamVideoAdd._add_4_with_4``. **
        """
        return _StreamVideoAdd._add_4_with_4(ref.convert(4), other)

    @staticmethod
    def _add_4_with_1(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Pseudo alias to ``from movia.core.filters.basic.add._StreamVideoAdd._add_4_with_3``. **
        """
        return _StreamVideoAdd._add_4_with_3(ref, other.convert(3))

    @staticmethod
    def _add_4_with_2(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Pseudo alias to ``from movia.core.filters.basic.add._StreamVideoAdd._add_4_with_4``. **
        """
        return _StreamVideoAdd._add_4_with_3(ref, other.convert(4))

    @staticmethod
    def _add_4_with_3(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Add a bgr frame to the bgr alpha frame_ref. **

        Like ``from movia.core.filters.basic.add._StreamVideoAdd._add_2_with_1`` with 3 channels.
        """
        a_r = ref[..., 3].to(dtype=torch.float16) # a_r
        a_r /= 255.0 # a_r/255
        a_r = torch.unsqueeze(a_r, 2)
        color = ref[..., :3].to(dtype=torch.float16) # c_r
        c_o = other[..., :3].to(dtype=torch.float16) # c_o
        color -= c_o # c_r - c_o
        color *= a_r # a_r/255 * (c_r-c_o)
        color += c_o # a_r/255 * (c_r - c_o) + c_o = (c_r*a_r + c_o*(255-a_r))/255
        color = color.to(dtype=torch.uint8) # shape (height, width, 1)
        return FrameVideo(ref.time, color)

    @staticmethod
    def _add_4_with_4(ref: FrameVideo, other: FrameVideo) -> FrameVideo:
        """
        ** Add a bgr alpha frame to the bgr alpha frame_ref. **

        Like ``from movia.core.filters.basic.add._StreamVideoAdd._add_2_with_2`` with 3 channels.
        """
        a_r = ref[..., 3].to(dtype=torch.float16) # a_r
        a_r /= 255.0 # a_r/255
        a_r = torch.unsqueeze(a_r, 2)
        a_o = other[..., 3].to(dtype=torch.float16) # a_r
        a_o /= 255.0 # a_r/255
        a_o = torch.unsqueeze(a_o, 2)
        c_r = ref[..., :3].to(dtype=torch.float16) # c_r
        c_o = other[..., :3].to(dtype=torch.float16) # c_r

        alpha = a_r * a_o # a_r/255*a_o/255
        alpha = torch.neg(alpha, out=alpha) # -a_r/255*a_o/255
        alpha += a_o # a_o/255 - a_r/255*a_o/255 = a_o/255 * (255-a_r)/255
        color = c_o * alpha # c_o * a_o/255 * (255-a_r)/255
        color += c_r * a_r # (c_r * a_r/255) + (c_o * a_o/255 * (255-a_r)/255)
        alpha += a_r # a_r/255 + a_o/255 - a_r/255*a_o/255
        color /= alpha # (c_r*a_r/255+c_o*a_o/255*(255-a_r)/255) / (a_r/255+a_o/255-a_r/255*a_o/255)
        alpha *= 255.0 # 255*(a_r/255 + a_o/255 - a_r/255*a_o/255) = 255 - ((255-a_r)*(255-a_o))/255

        ref[..., :3] = color # cast automatic
        ref[..., 3] = torch.squeeze(alpha, 2) # cast automatic
        return ref

    def _snapshot(self, timestamp: Fraction, shape: tuple[int, int]) -> FrameVideo:
        # selection of the concerned streams
        if not (
            streams := [
                s for s in self.node.in_streams if s.beginning <= timestamp < s.beginning+s.duration
            ]
        ):
            if timestamp < self.beginning or timestamp >= self.beginning + self.duration:
                raise OutOfTimeRange(
                    f"stream start {self.beginning} and end {self.beginning + self.duration}, "
                    f"no stream at timestamp {timestamp}"
                )
            return FrameVideo(
                timestamp, torch.zeros((*shape, 2), dtype=torch.uint8)
            )

        # general combinaison of the frames
        frame_ref = streams.pop(0)._snapshot(timestamp, shape)
        for stream in streams:
            # verif for avoid useless computing
            if frame_ref.channels in {1, 3}: # if no alpha channel
                return frame_ref
            if np.ma.allequal(frame_ref.numpy(force=True), 255):
                return frame_ref.convert(frame_ref.channels-1)
            # combination
            other = stream._snapshot(timestamp, shape)
            func_add = getattr(_StreamVideoAdd, f"_add_{frame_ref.channels}_with_{other.channels}")
            frame_ref =func_add(frame_ref, other)
        return frame_ref

    @property
    def beginning(self) -> Fraction:
        return min(s.beginning for s in self.node.in_streams)

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        end = max(s.beginning + s.duration for s in self.node.in_streams)
        return end - self.beginning

    @property
    def is_space_continuous(self) -> bool:
        if len(val := {s.is_space_continuous for s in self.in_streams}) != 1:
            raise AttributeError("combined streams are both space continuous and discrete")
        return val.pop()

    @property
    def is_time_continuous(self) -> bool:
        if len(val := {s.is_time_continuous for s in self.in_streams}) != 1:
            raise AttributeError("combined streams are both time continuous and discrete")
        return val.pop()


class _StreamAudioAdd(StreamAudio):
    """
    ** Concatenate and add the audio streams.**
    """

    def __init__(self, node: Node):
        """
        Parameters
        ----------
        node : movia.core.filters.basic.add.FilterAdd
            The node containing the StreamAudio to add.
        """
        assert isinstance(node, FilterAdd), node.__class__.__name__
        assert node.in_streams, "requires at least 1 audio stream to add"
        super().__init__(node)

    def _snapshot(self, timestamp: Fraction, rate: int, samples: int) -> FrameAudio:
        # selection of the concerned streams
        end = timestamp + Fraction(samples, rate) # apparition of last sample
        if timestamp < self.beginning or end > self.beginning + self.duration:
            raise OutOfTimeRange(
                f"stream start {self.beginning} and end {self.beginning + self.duration}, "
                f"no stream at timestamp {timestamp} to {timestamp} + {samples}/{rate}"
            )
        streams = [
            s for s in self.node.in_streams
            if end > s.beginning and timestamp < s.beginning + s.duration
        ]

        # slices selection
        slices = [
            (
                max(s.beginning, timestamp),
                min(s.beginning+s.duration, end)
            )
            for s in streams
        ]
        slices = [(start, math.floor(rate*(end_-start))) for start, end_ in slices]
        slices = [
            (stream, start, samples)
            for stream, (start, samples) in zip(streams, slices)
            if samples > 0
        ]

        # frames portion recuperations
        frames = [stream._snapshot(start, rate, samples) for stream, start, samples in slices]
        if len(channels := {frame.channels for frame in frames}) > 1:
            raise RuntimeError(
                f"impossible to combine frames of different channels {channels} "
                f"at timestamp {timestamp} to {timestamp} + {samples}/{rate}"
            )
        channels = channels.pop() if channels else 1

        # create the new empty audio frame
        dtypes = {frame.dtype for frame in frames}
        dtypes = sorted(
            dtypes, key=lambda t: {torch.float16: 2, torch.float32: 1, torch.float64: 0}[t]
        ) + [torch.float32] # if slice = []
        frame = FrameAudio(
            timestamp, rate, torch.full((channels, samples), torch.nan, dtype=dtypes[0])
        )

        # frames addition
        for frame_ in frames:
            start = math.floor(rate * (frame_.time-timestamp))
            part = frame[:, start:start+frame_.samples]
            part = torch.where(torch.isnan(part), frame_, part+frame_)
            frame[:, start:start+frame_.samples] = part
        return frame

    @property
    def beginning(self) -> Fraction:
        return min(s.beginning for s in self.node.in_streams)

    @property
    def channels(self) -> int:
        if len(channels := {s.channels for s in self.node.in_streams}) != 1:
            raise AttributeError(f"add streams do not have same channels {channels}")
        return channels.pop()

    @property
    def duration(self) -> typing.Union[Fraction, float]:
        end = max(s.beginning + s.duration for s in self.node.in_streams)
        return end - self.beginning

    @property
    def is_time_continuous(self) -> bool:
        if len(val := {s.is_time_continuous for s in self.node.in_streams}) != 1:
            raise AttributeError("combined streams are both time continuous and discrete")
        return val.pop()
