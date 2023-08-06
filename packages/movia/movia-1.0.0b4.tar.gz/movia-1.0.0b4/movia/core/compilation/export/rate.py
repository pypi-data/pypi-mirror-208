#!/usr/bin/env python3

"""
** Allows to suggest an appropriate rate. **
--------------------------------------------
"""

from fractions import Fraction

from movia.core.analysis.stream.rate_audio import optimal_rate_audio
from movia.core.analysis.stream.rate_video import optimal_rate_video
from movia.core.classes.stream_audio import StreamAudio
from movia.core.classes.stream_video import StreamVideo
from movia.core.compilation.export.compatibility import CodecInfos, EncoderInfos, WriteInfos
from movia.core.exceptions import IncompatibleSettings



def _available_audio_rates(encodec: str) -> set[str]:
    """
    ** Search the different sampling frequencies available by this encodec. **

    No verification are performed for performance reason.
    """
    if encodec in WriteInfos().encoders:
        encoders = {encodec}
    else:
        encoders = CodecInfos(encodec).encoders
    choices = [EncoderInfos(enc).rates for enc in encoders]
    choices = [rates for rates in choices if rates]
    if choices:
        if not (choices := set.intersection(*choices)):
            raise IncompatibleSettings(
                f"the {encoders} encoders of the '{encodec}' codec "
                "do not have a common rate, you must specify an encoder to remove the ambiguity"
            )
        return choices
    return set()


def suggest_audio_rate(stream: StreamAudio, encodec: str="default") -> int:
    """
    ** Returns the best compatible audio samplerate. **

    Parameters
    ----------
    stream : movia.core.classes.stream_audio.StreamAudio
        The stream that we want to encode.
    encodec : str, optional
        The encodec used, the value "default" means not to take it into account.
    Returns
    -------
    rate : int
        A suitable sampling rate compatible with the specified encodec.

    Examples
    --------
    >>> from movia.core.compilation.export.rate import suggest_audio_rate
    >>> from movia.core.io.read import ContainerInputFFMPEG
    >>> (stream,) = ContainerInputFFMPEG("movia/examples/audio.ogg").out_streams
    >>> suggest_audio_rate(stream) # no constraint
    16000
    >>> suggest_audio_rate(stream, "ac3") # only 32000, 44100 and 48000 available
    32000
    >>>
    """
    assert isinstance(stream, StreamAudio), stream.__class__.__name__
    assert isinstance(encodec, str), encodec.__class__.__name__

    # determine choices
    if encodec != "default":
        choices = _available_audio_rates(encodec) or None
    else:
        choices = None # means all possibilities

    # determine rate
    return optimal_rate_audio(stream, choices=choices) or 48000


def suggest_video_rate(stream: StreamVideo) -> Fraction:
    """
    ** Returns the best compatible video framerate. **

    Parameters
    ----------
    stream : movia.core.classes.stream_video.StreamVideo
        The stream that we want to encode.
    Returns
    -------
    rate : Fraction
        An optimal frame rate.

    Examples
    --------
    >>> from movia.core.compilation.export.rate import suggest_video_rate
    >>> from movia.core.io.read import ContainerInputFFMPEG
    >>> (stream,) = ContainerInputFFMPEG("movia/examples/video.mp4").out_streams
    >>> suggest_video_rate(stream)
    Fraction(25, 1)
    >>>
    """
    return optimal_rate_video(stream) or Fraction(30000, 1001)
