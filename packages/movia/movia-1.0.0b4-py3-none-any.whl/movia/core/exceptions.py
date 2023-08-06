#!/usr/bin/env python3

"""
** Groups the exceptions specific to ``movia``. **
--------------------------------------------------

Rather than returning too general exceptions, these exceptions allow a much more precise debugging.
"""



class MoviaException(Exception):
    """
    ** Base class for exceptions specific to this module. **
    """


class MissingFrameError(MoviaException, OSError):
    """
    ** When a frame is missing in a stream. **

    This exception can be thrown if the reded frames have a strange behavior.
    """


class MissingInformation(MoviaException, ValueError):
    """
    ** When information is unreadable or missing from the metadata. **

    It can be raised when trying to access a tag that is not defined
    or that returns a surprising value.
    """


class MissingStreamError(MoviaException, OSError):
    """
    ** When a stream is missing in a file. **

    This exception can be raised when looking for a video,
    audio or image stream in a media that does not contain any or that is unreadable.
    """


class OutOfTimeRange(MoviaException, EOFError):
    """
    ** Access outside the definition range **

    This exception is raised when accessing or writing
    outside the range in which the stream is defined.
    """

class IncompatibleSettings(MoviaException, RuntimeError):
    """
    ** When parameters are incompatible with each other. **

    This exception may mean that a choice is not possible.
    """
