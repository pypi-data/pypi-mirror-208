#!/usr/bin/env python3

"""
** Allows to suggest an appropriate encoder. **
-----------------------------------------------
"""

import itertools

from movia.core.classes.stream import Stream
from movia.core.compilation.export.compatibility import CodecInfos, WriteInfos



def suggest_encodec(stream: Stream, stream_settings: dict, muxer: str) -> str:
    """
    ** Returns the name of an ffmpeg container format appropriate for the given parameters. **

    Parameters
    ----------
    stream : movia.core.classes.stream.Stream
        The stream that we want to encode.
    stream_settings : dict
        The parameters of the stream in question,
        provided by ``movia.core.compilation.export.default.suggest_export_params``.
    muxer : str
        The name of the muxer ffmpeg, it is call "format" in pyav and in returs parameters.

    Returns
    -------
    encodec : str
        An encoder compatible with the provided context.
    """
    assert isinstance(stream, Stream), stream.__class__.__name__
    assert isinstance(stream_settings, dict), stream_settings.__class__.__name__
    assert isinstance(muxer, str), muxer.__class__.__name__

    write_infos = WriteInfos()
    codecs = sorted(c for c in write_infos.codecs if CodecInfos(c).type == stream.type)

    if stream.type == "audio":
        defaults = ("libopus", "ac3", "aac", "vorbis", "mp3")
    elif stream.type == "video":
        defaults = ("av1", "hevc", "h264", "mjpeg")
    else:
        raise TypeError(f"not yet supported {stream.type}")
    for codec in itertools.chain(defaults, codecs):
        if write_infos.check_compatibilities([codec], [muxer]).item():
            return codec
    raise RuntimeError(f"no encodecs found for the stream {stream} with the muxer {muxer}")
