#!/usr/bin/env python3

"""
** Find the default settings for ``movia.core.io.write.ContainerOutputFFMPEG``. **
----------------------------------------------------------------------------------
"""

import pathlib

from movia.core.analysis.stream.shape import optimal_shape_video
from movia.core.classes.stream import Stream
from movia.core.compilation.export.compatibility import MuxerInfos
from movia.core.compilation.export.encodec import suggest_encodec
from movia.core.compilation.export.muxer import suggest_muxer
from movia.core.compilation.export.rate import suggest_audio_rate
from movia.core.compilation.export.rate import suggest_video_rate



def suggest_export_params(
    in_streams: tuple[Stream],
    *,
    filename: pathlib.Path,
    streams_settings: list[dict],
    container_settings: dict,
):
    """
    ** Suggests a combination of suitable parameters. **

    Parameters
    ----------
    in_streams : tuple[movia.core.classes.stream.Stream]
        The ordered streams to be encoded.
    filename : pathlike, optional
        The final file, relative or absolute.
        If the suffix is provided, it allows to find the muxer (if it is not already provided).
        If the muxer is provided, the associated suffix is added to the file name
        (if the filename has no suffix)
    streams_settings: list[dict]
        As the input parameter `streams_settings` of the class
        ``movia.core.io.write.ContainerOutputFFMPEG`` with "default" string values
        where you have to look for a suitable parameter.
    container_settings: dict
        As the input parameter `container_settings` of the class
        ``movia.core.io.write.ContainerOutputFFMPEG`` with "default" string values
        where you have to look for a suitable parameter.

    Returns
    -------
    filename : pathlib.Path
        A default file name with the appropriate suffix.
    streams_settings : list[dict]
        Same structure as the input parameter but with the
        "default" fields replaced by their final value.
    container_settings : dict
        Same structure as the input parameter but with the
        "default" fields replaced by their final value.
    """
    assert isinstance(in_streams, tuple), in_streams.__class__.__name__
    assert all(isinstance(s, Stream) for s in in_streams), in_streams
    assert isinstance(filename, pathlib.Path), filename.__class__.__name__
    assert isinstance(streams_settings, list), streams_settings.__class__.__name__
    assert all(isinstance(s, dict) for s in streams_settings), streams_settings
    assert len(streams_settings) == len(in_streams), (streams_settings, in_streams)
    assert isinstance(container_settings, dict), container_settings.__class__.__name__

    # find muxer if no suffix and no muxer provide
    if not filename.suffix and container_settings["format"] == "default":
        container_settings["format"] = suggest_muxer()

    # add suffix if muxer is given
    if not filename.suffix and container_settings["format"] != "default":
        if (extensions := MuxerInfos(container_settings["format"]).extensions):
            filename = filename.with_suffix(sorted(extensions)[0])

    # find muxer if suffix is given
    if filename.suffix and container_settings["format"] == "default":
        container_settings["format"] = MuxerInfos.from_suffix(filename.suffix)

    # find encodec if not provide
    for stream, stream_settings in zip(in_streams, streams_settings):
        if stream_settings["encodec"] == "default":
            stream_settings["encodec"] = (
                suggest_encodec(stream, stream_settings, container_settings["format"])
            )

    # shape
    for stream, stream_settings in zip(in_streams, streams_settings):
        if stream.type != "video" or stream_settings.get("shape") != "default":
            continue
        stream_settings["shape"] = list(optimal_shape_video(stream) or (1080, 1920))

    # rate
    for stream, stream_settings in zip(in_streams, streams_settings):
        if stream.type == "audio" and stream_settings.get("rate") == "default":
            stream_settings["rate"] = suggest_audio_rate(
                stream,
                stream_settings.get("encodec", "default"),
            )
        elif stream.type == "video" and stream_settings.get("rate") == "default":
            stream_settings["rate"] = str(suggest_video_rate(stream))

    return filename, streams_settings, container_settings
