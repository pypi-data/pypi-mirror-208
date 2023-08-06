#!/usr/bin/env python3

"""
** General node of the assembly graph. **
-----------------------------------------
"""

import abc
import typing

from movia.core.classes.stream import Stream



class Node(abc.ABC):
    """
    ** General node of the assembly graph. **

    Parameters
    ----------
    in_streams : tuple[Stream, ...]
        The streams arriving on the node (readonly).
    out_streams : tuple[Stream, ...]
        The streams coming back on the node (readonly).
    """

    def __init__(self, in_streams: typing.Iterable[Stream], out_streams: typing.Iterable[Stream]):
        assert hasattr(in_streams, "__iter__"), in_streams.__class__.__name__
        in_streams = tuple(in_streams)
        assert all(isinstance(stream, Stream) for stream in in_streams), \
            [stream.__class__.__name__ for stream in in_streams]
        assert hasattr(out_streams, "__iter__"), out_streams.__class__.__name__
        out_streams = tuple(out_streams)
        assert all(isinstance(stream, Stream) for stream in out_streams), \
            [stream.__class__.__name__ for stream in out_streams]
        self._in_streams = in_streams
        self._out_streams = out_streams

    def __eq__(self, other) -> bool:
        """
        ** Check that 2 nodes are equivalent. **
        """
        if self.__class__ != other.__class__:
            return False
        if self.getstate() != other.getstate():
            return False
        if self.in_streams != other.in_streams:
            return False # not compare out_streams to avoide infinite loop
        return True

    def __getstate__(self) -> tuple[typing.Iterable[Stream], dict]:
        """
        ** Allow ``pickle`` to serialize efficiently. **
        """
        return self.in_streams, self.getstate()

    def __setstate__(self, streams_state) -> None:
        """
        ** Allows ``pickle`` to recreate the object identically. **

        Parameters
        ----------
        streams_state : tuple[typing.Iterable[movia.core.classes.stream.Stream], dict]
            These are the input streams and the other arguments.
        """
        assert isinstance(streams_state, tuple), streams_state.__class__.__name__
        assert len(streams_state) == 2, streams_state
        in_streams, state = streams_state
        self.setstate(in_streams, state)

    @classmethod
    @abc.abstractmethod
    def default(cls):
        """
        ** Provide an example of an instance of this node. **

        Returns
        -------
        example : Node
            An example of an instance of this class.

        Notes
        -----
        It is a ``classmethod`` rather than a ``staticmethod`` in order to simplify inheritance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def getstate(self) -> dict:
        """
        ** Retrieves the internal state of the object. **

        Returns
        -------
        state : dict
            An explicit dictionary containing the different attributes of the object.
            This dictionary must be fully serializable by pickle.
            Even if this is not optimal in terms of memory and speed,
            the objects must be explicit so that they can be easily manipulated
            when the assembly graph is optimized.
            The keys must be of type str and the dictionary must to be jsonisable.
        """
        raise NotImplementedError

    def in_select(self, type_: str) -> tuple[Stream, ...]:
        """
        ** Select the incoming streams of a specific type. **
        """
        assert isinstance(type_, str), type_.__class__.__name__
        return tuple(s for s in self._in_streams if s.type == type_)

    @property
    def in_streams(self) -> tuple[Stream, ...]:
        """
        ** The incoming streams on the node. **
        """
        return self._in_streams

    def out_select(self, type_: str) -> tuple[Stream, ...]:
        """
        ** Select the outgoing streams of a specific type. **
        """
        assert isinstance(type_, str), type_.__class__.__name__
        return tuple(s for s in self._out_streams if s.type == type_)

    @property
    def out_streams(self) -> tuple[Stream, ...]:
        """
        ** The outgoing streams on the node. **
        """
        return self._out_streams

    @abc.abstractmethod
    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        """
        ** Allows to completely change the internal state of the node. **

        Parameters
        ----------
        in_streams
            Same as ``movia.core.classes.stream.Stream.in_streams``.
        state : dict
            The internal state returned by the ``getstate`` method of the same class.
        """
        raise NotImplementedError
