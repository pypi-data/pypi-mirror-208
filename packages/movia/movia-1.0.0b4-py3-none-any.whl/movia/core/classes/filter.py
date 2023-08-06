#!/usr/bin/env python3

"""
** It's a node that acts on streams. **
---------------------------------------
"""

import typing

from movia.core.classes.node import Node
from movia.core.classes.stream import Stream



class Filter(Node):
    """
    ** This is a filter that applies to several streams. **

    A filter can be empty, i.e. have no input and no output streams.
    On the other hand, it cannot have an input stream but no output stream,
    or an output stream but no input stream.
    """

    def __init__(self, in_streams: typing.Iterable[Stream], out_streams: typing.Iterable[Stream]):
        super().__init__(in_streams, out_streams)
        assert len(self.in_streams) != 0 or len(self.out_streams) == 0, \
            "an effect with no input flow, must have no output flow"
        assert len(self.in_streams) == 0 or len(self.out_streams) != 0, \
            "an effect with at least one input stream, must have at least one output stream"
