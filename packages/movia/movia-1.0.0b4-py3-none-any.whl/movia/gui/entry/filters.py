#!/usr/bin/env python3

"""
** Allows to view and add all generators. **
--------------------------------------------
"""

from movia.core.classes.filter import Filter
from movia.gui.entry.base import Entry


class Filters(Entry):
    """
    ** Filters visualization window. **
    """

    def __init__(self, parent):
        super().__init__(parent, ["filters"], {"Filter", "MetaFilter"}, Filter)
