#!/usr/bin/env python3

"""
** Defines the entry and exit points of the assembly graph. **
--------------------------------------------------------------
"""

import typing

from movia.core.classes.node import Node
from movia.core.classes.stream import Stream



class ContainerInput(Node):
    """
    ** Entry point of an assembly graph. **
    """

    def __init__(self, out_streams: typing.Iterable[Stream]):
        super().__init__((), out_streams)
        assert len(self.out_streams) != 0, "at least one flow must leave in the input container"


class ContainerOutput(Node):
    """
    ** Coming back point of an assembly graph. **
    """

    def __init__(self, in_streams: typing.Iterable[Stream]):
        super().__init__(in_streams, ())
        assert len(self.in_streams) != 0, "at least one flow must arrive in the output container"

    @classmethod
    def default(cls):
        raise NotImplementedError

    def getstate(self) -> dict:
        return {}

    def setstate(self, in_streams: typing.Iterable[Stream], state: dict) -> None:
        assert state == {}, state
        ContainerOutput.__init__(self, in_streams)

    def write(self):
        """
        ** Runs the complete assembly graph and exploite the last streams. **
        """
        raise NotImplementedError
