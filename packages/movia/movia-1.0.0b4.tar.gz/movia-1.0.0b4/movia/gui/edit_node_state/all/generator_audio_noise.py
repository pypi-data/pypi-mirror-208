#!/usr/bin/env python3

"""
** Properties of a ``movia.core.generation.audio.noise.GeneratorAudioNoise``. **
--------------------------------------------------------------------------------
"""

from PyQt6 import QtWidgets

from movia.gui.edit_node_state.base import EditBase
from movia.gui.edit_node_state.interface import Seedable



class EditGeneratorAudioNoise(EditBase):
    """
    ** Allows to view and modify the properties of a generator of type ``GeneratorAudioNoise``.
    """

    def __init__(self, parent, node_name):
        EditBase.__init__(self, parent, node_name)
        grid_layout = QtWidgets.QGridLayout()
        Seedable(self)(grid_layout)
        self.setLayout(grid_layout)
