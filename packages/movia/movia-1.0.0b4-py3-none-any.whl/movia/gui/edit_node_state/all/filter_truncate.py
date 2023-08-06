#!/usr/bin/env python3

"""
** Properties of a ``movia.core.filter.basic.truncate.FilterTruncate``. **
--------------------------------------------------------------------------
"""

from fractions import Fraction

from PyQt6 import QtWidgets

from movia.gui.edit_node_state.base import EditBase



class EditFilterTruncate(EditBase):
    """
    ** Allows to view and modify the properties of a filter of type ``FilterTruncate``.
    """

    def __init__(self, parent, node_name):
        super().__init__(parent, node_name)
        self._duration_max_textbox = QtWidgets.QLineEdit(self)

        grid_layout = QtWidgets.QGridLayout()
        self.init_duration_max(grid_layout)
        self.setLayout(grid_layout)

    def _validate_duration_max(self, text):
        """
        ** Check that the av kwargs are correct and update the color. **
        """
        try:
            duration_max = Fraction(text)
        except ValueError:
            self._duration_max_textbox.setStyleSheet("background:red;")
            return
        self.try_set_state(
            self.get_new_state({"duration_max": str(duration_max)}), self._duration_max_textbox
        )

    def init_duration_max(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the av kwargs. **
        """
        grid_layout.addWidget(QtWidgets.QLabel("Duration Max (second):"))
        self._duration_max_textbox.setText(self.state["duration_max"])
        self._duration_max_textbox.textChanged.connect(self._validate_duration_max)
        grid_layout.addWidget(self._duration_max_textbox, ref_span, 1)
        return ref_span + 1
