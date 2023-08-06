#!/usr/bin/env python3

"""
** Allows you to avoid redundancy in the node editing windows. **
-----------------------------------------------------------------

Defines several accessors that allow to lighten the code of child classes.
This is also where methods common to several classes are implemented to avoid data redundancy.
"""

from PyQt6 import QtWidgets

from movia.gui.edit_node_state.base import EditBase



class Seedable:
    """
    ** Allows you to manage a `seed` field. **

    It is a float between [0, 1[.
    """

    def __init__(self, edit: EditBase):
        assert isinstance(edit, EditBase), edit.__class__.__name__
        assert "seed" in edit.state, sorted(edit.state)
        self.edit = edit
        self.edit.ref.append(self)
        self.textbox = QtWidgets.QLineEdit(edit)

    def __call__(self, grid_layout: QtWidgets.QGridLayout, ref_span=0):
        """
        ** Displays and allows to modify the av kwargs. **
        """
        assert isinstance(grid_layout, QtWidgets.QGridLayout), grid_layout.__class__.__name__
        grid_layout.addWidget(QtWidgets.QLabel("Seed (0 <= float < 1):", self.edit))
        self.textbox.setText(str(self.edit.state["seed"]))
        self.textbox.textChanged.connect(self.validate)
        grid_layout.addWidget(self.textbox, ref_span, 1)
        ref_span += 1
        return ref_span

    def validate(self, text):
        """
        ** Check that the seed is a float in [0, 1[. **,
        """
        try:
            seed = float(text)
        except ValueError:
            self.textbox.setStyleSheet("background:red;")
            return
        if seed < 0 or seed >= 1:
            self.textbox.setStyleSheet("background:red;")
            return

        self.edit.try_set_state(self.edit.get_new_state({"seed": seed}), self.textbox)
