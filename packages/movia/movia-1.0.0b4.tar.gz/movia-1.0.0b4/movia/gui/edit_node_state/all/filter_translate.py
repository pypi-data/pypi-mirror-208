#!/usr/bin/env python3

"""
** Properties of a ``movia.core.filter.basic.truncate.FilterTruncate``. **
--------------------------------------------------------------------------
"""

from fractions import Fraction
import math

from PyQt6 import QtWidgets

from movia.gui.edit_node_state.base import EditBase



class EditFilterTranslate(EditBase):
    """
    ** Allows to view and modify the properties of a filter of type ``FilterTranslate``.
    """

    def __init__(self, parent, node_name):
        super().__init__(parent, node_name)
        self._delay_textbox = QtWidgets.QLineEdit(self)

        grid_layout = QtWidgets.QGridLayout()
        self.init_delay(grid_layout)
        self.setLayout(grid_layout)

    def _validate_delay(self, text):
        """
        ** Check that the av kwargs are correct and update the color. **
        """
        delay = {"inf": math.inf, "oo": math.inf}.get(text, text)
        try:
            delay = Fraction(delay)
        except OverflowError:
            pass
        except ValueError:
            self._delay_textbox.setStyleSheet("background:red;")
            return
        else:
            delay = str(delay)

        self.try_set_state(self.get_new_state({"delay": delay}), self._delay_textbox)


    def init_delay(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the av kwargs. **
        """
        grid_layout.addWidget(QtWidgets.QLabel("Delay (second):"))
        self._delay_textbox.setText(self.state["delay"])
        self._delay_textbox.textChanged.connect(self._validate_delay)
        grid_layout.addWidget(self._delay_textbox, ref_span, 1)
        return ref_span + 1
