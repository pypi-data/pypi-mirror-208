#!/usr/bin/env python3

"""
** Allows you to temporarily concatenate several streams. **
------------------------------------------------------------
"""

import logging
import math
import typing

from movia.core.classes.meta_filter import MetaFilter
from movia.core.classes.node import Node
from movia.core.classes.stream import Stream
from movia.core.filters.basic.add import FilterAdd
from movia.core.filters.basic.translate import FilterTranslate



class FilterChain(MetaFilter):
    """
    ** Concatenate the streams end-to-end. **

    Examples
    --------
    >>> import torch
    >>> from movia.core.filters.basic.chain import FilterChain
    >>> from movia.core.filters.basic.truncate import FilterTruncate
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.generation.video.noise import GeneratorVideoNoise
    >>>
    >>> (s_audio_0,) = FilterTruncate(GeneratorAudioNoise(0).out_streams, 10).out_streams
    >>> (s_audio_1,) = GeneratorAudioNoise(.5).out_streams
    >>> (s_chain_audio,) = FilterChain([s_audio_0, s_audio_1]).out_streams
    >>> (s_video_0,) = FilterTruncate(GeneratorVideoNoise(0).out_streams, 10).out_streams
    >>> (s_video_1,) = GeneratorVideoNoise(.5).out_streams
    >>> (s_chain_video,) = FilterChain([s_video_0, s_video_1]).out_streams
    >>>
    >>> (
    ...     s_chain_audio.snapshot(0, 1, 20) == torch.cat(
    ...         (s_audio_0.snapshot(0, 1, 10), s_audio_1.snapshot(0, 1, 10)), axis=1
    ...     )
    ... ).all()
    tensor(True)
    >>> (s_video_0.snapshot(0, (2, 2)) == s_chain_video.snapshot(0, (2, 2))).all()
    tensor(True)
    >>> (s_video_1.snapshot(0, (2, 2)) == s_chain_video.snapshot(10, (2, 2))).all()
    tensor(True)
    >>> (s_video_1.snapshot(10, (2, 2)) == s_chain_video.snapshot(20, (2, 2))).all()
    tensor(True)
    >>>
    """

    def _compile(self, in_streams: tuple[Stream]) -> Node:
        streams = [in_streams[0]] # can not raise IndexError because none empty
        pos = streams[0].beginning + streams[0].duration
        for i, stream in enumerate(in_streams[1:]):
            if pos == math.inf:
                logging.warning("the stream %i is infinite, can not chain an other stream after", i)
                break
            streams.append(FilterTranslate([stream], pos - stream.beginning).out_streams[0])
            pos += stream.duration
        return FilterAdd(streams)

    @classmethod
    def default(cls):
        return cls([])

    def getstate(self) -> dict:
        return {}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}
        FilterChain.__init__(self, in_streams)
