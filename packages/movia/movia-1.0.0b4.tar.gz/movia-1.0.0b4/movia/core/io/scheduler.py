#!/usr/bin/env python3

"""
** Combines several stream to yield frame in monotonic order. **
----------------------------------------------------------------

It is helpfull for writing and muxing.
"""

from fractions import Fraction
import functools
import itertools
import logging
import math
import typing

import numpy as np
import torch

from movia.core.classes.frame import Frame
from movia.core.classes.frame_audio import FrameAudio
from movia.core.classes.frame_video import FrameVideo
from movia.core.classes.stream import Stream
from movia.core.classes.stream_audio import StreamAudio
from movia.core.classes.stream_video import StreamVideo
from movia.core.exceptions import MissingStreamError, OutOfTimeRange
from movia.core.optimisation.parallel.buffer import imap, starimap



def _raise_missing_stream_error(gen: typing.Iterable) -> typing.Iterable:
    """
    ** Decorator that raises MissingStreamError if the gen yields nothing. **
    """
    @functools.wraps(gen)
    def generator(*args, **kwargs):
        empty = True
        for res in gen(*args, **kwargs):
            empty = False
            yield res
        if empty:
            raise MissingStreamError("no frame is present in any of the streams")
    return generator


def audio_frames_async(
    stream: StreamAudio,
    rate: typing.Union[Fraction, int],
    start_time: Fraction,
    samples: typing.Optional[int]=None,
    **_
) -> typing.Iterable[FrameAudio]:
    """
    ** Decodes the audio frames in an over thread for performance. **

    Parameters
    ----------
    stream : movia.core.classes.stream_audio.StreamAudio
        The audio stream for extract the frames.
    rate : int
        The time frequency between each samples to catch.
    start_time : fraction.Fraction
        The frame with start time < start_time are ignored.
    samples : int, default=4096
        The maximum number of samples in a frame. The last frame
        can to contains less samples in order to reach the end.
        The special default value None means to choose automaticaly the
        optimal number of samples in accordance to the sample rate.

    Yields
    ------
    movia.core.classes.frame_audio.FrameAudio
        The frame audio such as create the complete signal if we concatenate her.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.filters.basic.truncate import FilterTruncate
    >>> from movia.core.io.scheduler import audio_frames_async
    >>>
    >>> (stream,) = FilterTruncate(GeneratorAudioNoise.default().out_streams, 1).out_streams
    >>> for frame in audio_frames_async(stream, 1000, Fraction(10, 1001), samples=200):
    ...     frame.time, frame.samples
    ...
    (Fraction(1, 100), 200)
    (Fraction(21, 100), 200)
    (Fraction(41, 100), 200)
    (Fraction(61, 100), 200)
    (Fraction(81, 100), 190)
    >>>
    """
    assert isinstance(stream, StreamAudio), stream.__class__.__name__
    if isinstance(rate, Fraction):
        assert rate.denominator == 1, f"{rate} has to be integer"
        rate = int(rate)
    assert isinstance(rate, int), rate.__class__.__name__
    assert rate > 0, rate # avoid stationnary 0 and backward
    assert isinstance(start_time, Fraction), start_time.__class__.__name__
    if samples is None:
        samples = 2**round(math.log(max(1, rate*100e-3), 2)) # approx 100 ms
    assert isinstance(samples, int), samples.__class__.__name__
    assert samples >= 1, samples

    def _snapshot(arg):
        stream, timestamp, rate, samples = arg

        # extraction
        try:
            frame = stream.snapshot(timestamp, rate, samples)
        except OutOfTimeRange as err: # end is near
            end = stream.beginning + stream.duration
            samples_frac = (end - timestamp) * rate
            if (samples := math.floor(samples_frac)) <= 0:
                raise err
            frame = stream.snapshot(timestamp, rate, samples)

        # verification
        min_val, max_val = torch.aminmax(frame)
        if min_val.item() < -1 or max_val.item() > 1:
            logging.warning(
                "saturated samples detected min %f max %f", min_val.item(), max_val.item()
            )
        return frame

    start_time = max(start_time, stream.beginning) # avoid OutOfTimeRange for t < beginning
    if rest := start_time % Fraction(1, rate):
        start_time += Fraction(1, rate) - rest # start_time = k*(1/sr), k integer
    interval = Fraction(samples, rate)

    try:
        yield from imap(
            _snapshot,
            ((stream, start_time + i*interval, rate, samples) for i in itertools.count())
        )
    except OutOfTimeRange:
        pass


def video_frames_async(
    stream: StreamVideo, out_fps: Fraction, start_time: Fraction, shape: tuple[int, int], **_
) -> typing.Iterable[FrameVideo]:
    """
    ** Decodes the video frames in an over thread for performance. **

    Parameters
    ----------
    stream : movia.core.classes.stream_video.StreamVideo
        The video stream for extract the frames.
    out_fps : Fraction
        The 1/step interval for each frame timestamp request.
    start_time : Fraction
        The frame with timestamp < start_time are ignored.
    shape : tuple[int, int]
        Transmitted to ``mocia.core.classes.stream_video.snapshot``.

    Yields
    ------
    movia.core.classes.frame_video.FrameVideo
        The frame videos in monotonic (non strict) order.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>> from movia.core.filters.basic.truncate import FilterTruncate
    >>> from movia.core.io.scheduler import video_frames_async
    >>>
    >>> (stream,) = FilterTruncate(GeneratorVideoNoise.default().out_streams, 1).out_streams
    >>> for frame in video_frames_async(stream, Fraction(10, 1), Fraction(99, 200), shape=(1, 1)):
    ...     frame.time
    ...
    Fraction(1, 2)
    Fraction(3, 5)
    Fraction(7, 10)
    Fraction(4, 5)
    Fraction(9, 10)
    >>>
    """
    assert isinstance(stream, StreamVideo), stream.__class__.__name__
    assert isinstance(out_fps, Fraction), out_fps.__class__.__name__
    assert out_fps > 0, out_fps # avoid division by 0 and backward
    assert isinstance(start_time, Fraction), start_time.__class__.__name__
    assert isinstance(shape, tuple), shape.__class__.__name__
    assert len(shape) == 2, len(shape)
    assert all(isinstance(s, int) and s >= 1 for s in shape), shape

    start_time = max(start_time, stream.beginning) # avoid OutOfTimeRange for t < beginning
    if rest := start_time % (1/out_fps):
        start_time += 1/out_fps - rest # start_time = k*(1/fps), k integer

    try:
        yield from starimap(
            stream.snapshot, ((start_time + i/out_fps, shape) for i in itertools.count())
        )
    except OutOfTimeRange:
        pass


@_raise_missing_stream_error
def scheduler(
    streams: list[Stream],
    rates: list[typing.Union[Fraction, int]],
    start_time: Fraction=Fraction(0),
    shapes: typing.Union[None, tuple[int, int], list[typing.Union[None, tuple[int, int]]]]=None,
    **kwargs,
) -> typing.Iterable[tuple[int, Frame]]:
    """
    ** Extract in chronological order the frames of all flows. **

    Gives up frames until all streams have raised the OutOfTimeRange exception.

    Parameters
    ----------
    streams : list[movia.core.classes.stream.Stream]
        Audio or video streams to exract the frames.
    rates : list[Fraction]
        The frame rate for video streams and the sample rate for audio streams.
    start_time : Fraction, default=0
        The position of the first frame yielded. The frame before are ignored.
    shape[s] : tuple[int, int] or list[tuple[int, int]], optinal
        For video only, ignore if there is no video stream.
        Each shape are transmitted to the stream. If the list is not provided,
        the same shape is transmitted to all video streams.
    **kwargs : dict
        Transmitted to the functions ``movia.core.io.scheduler.audio_frames_async``
        and ``movia.core.io.scheduler.video_frames_async``.

    Yields
    ------
    index : int
        The index of the concerned stream in the order of the provided list.
    frame : movia.core.classes.frame.Frame
        The future frame of the stream considered.
        The ``time`` attribute is guaranteed to be monotonic.

    Raises
    ------
    movia.core.exceptions.MissingStreamError
        If no frame are yielded.

    Examples
    --------
    >>> from fractions import Fraction
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>> from movia.core.filters.basic.truncate import FilterTruncate
    >>> from movia.core.io.scheduler import scheduler
    >>>
    >>> s_1 = FilterTruncate(GeneratorVideoNoise.default().out_streams, Fraction(1, 10)).out_streams
    >>> s_2 = FilterTruncate(GeneratorVideoNoise.default().out_streams, Fraction(1, 4)).out_streams
    >>> streams_video = [s_1[0], s_2[0]]
    >>> rates_video = [Fraction(30), Fraction(24)]
    >>> s_3 = FilterTruncate(GeneratorAudioNoise.default().out_streams, Fraction(1, 10)).out_streams
    >>> s_4 = FilterTruncate(GeneratorAudioNoise.default().out_streams, Fraction(1, 4)).out_streams
    >>> streams_audio = [s_3[0], s_4[0]]
    >>> rates_audio = [96000, 48000]
    >>>
    >>> # test audio only
    >>> for index, frame in scheduler(streams_audio, rates_audio):
    ...     index, frame.time
    ...
    (0, Fraction(0, 1))
    (1, Fraction(0, 1))
    (0, Fraction(32, 375))
    (1, Fraction(32, 375))
    (1, Fraction(64, 375))
    >>> for index, frame in scheduler(streams_audio, rates_audio, start_time=Fraction(1, 10)):
    ...     index, frame.time
    ...
    (1, Fraction(1, 10))
    (1, Fraction(139, 750))
    >>>
    >>> # test video only
    >>> for index, frame in scheduler(streams_video, rates_video, shape=(1, 1)):
    ...     index, frame.time
    ...
    (0, Fraction(0, 1))
    (1, Fraction(0, 1))
    (0, Fraction(1, 30))
    (1, Fraction(1, 24))
    (0, Fraction(1, 15))
    (1, Fraction(1, 12))
    (1, Fraction(1, 8))
    (1, Fraction(1, 6))
    (1, Fraction(5, 24))
    >>> for index, frame in scheduler(streams_video, rates_video, Fraction(1, 10), shape=(1, 1)):
    ...     index, frame.time
    ...
    (1, Fraction(1, 8))
    (1, Fraction(1, 6))
    (1, Fraction(5, 24))
    >>>
    >>> # test audio and video
    >>> for index, frame in scheduler(
    ...     streams_audio+streams_video, rates_audio+rates_video, shape=(1, 1), samples=4096
    ... ):
    ...     index, frame.time
    ...
    (0, Fraction(0, 1))
    (1, Fraction(0, 1))
    (2, Fraction(0, 1))
    (3, Fraction(0, 1))
    (2, Fraction(1, 30))
    (3, Fraction(1, 24))
    (0, Fraction(16, 375))
    (2, Fraction(1, 15))
    (3, Fraction(1, 12))
    (0, Fraction(32, 375))
    (1, Fraction(32, 375))
    (3, Fraction(1, 8))
    (3, Fraction(1, 6))
    (1, Fraction(64, 375))
    (3, Fraction(5, 24))
    >>>
    """
    assert isinstance(streams, list), streams.__class__.__name__
    assert all(isinstance(s, Stream) for s in streams), streams
    assert isinstance(rates, list), rates.__class__.__name__
    assert len(streams) == len(rates)
    if shapes is None:
        shapes = [None for _ in streams]
    elif isinstance(shapes, tuple):
        shapes = [shapes for _ in streams]
    else:
        assert isinstance(shapes, list), shapes.__class__.__name__
        assert len(streams) == len(shapes)

    buffer = [None for _ in range(len(streams))] # buffered frame for each stream
    queues = [
        iter(
            {"audio": audio_frames_async, "video": video_frames_async}[stream.type]
            (stream, rate, start_time, **{"shape": shape, **kwargs})
        )
        for stream, rate, shape in zip(streams, rates, shapes)
    ] # asynchroneous decoder of frame for each stream, None when exausted

    while any(q is not None for q in queues):
        index = [j for j in (i for i, q in enumerate(queues) if q is not None) if buffer[j] is None]
        try:
            index = index.pop() # search position of empty stream
        except IndexError: # in case we have to yield a frame
            index = np.argmin([f.time if f is not None else math.inf for f in buffer])
            yield index, buffer[index]
            buffer[index] = None
        else: # in case we need to recover a new frame
            try:
                buffer[index] = next(queues[index])
            except StopIteration:
                buffer[index] = queues[index] = None
