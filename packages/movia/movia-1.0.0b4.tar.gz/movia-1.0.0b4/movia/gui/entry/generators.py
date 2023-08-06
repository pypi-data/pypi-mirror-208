#!/usr/bin/env python3

"""
** Allows to view and add all generators. **
--------------------------------------------
"""

from movia.core.classes.container import ContainerInput
from movia.gui.entry.base import Entry



class Generators(Entry):
    """
    ** Generators visualization window. **
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            ["generation"],
            {"ContainerInput", "GeneratorAudioEmpty", "GeneratorVideoEmpty"},
            ContainerInput
        )
