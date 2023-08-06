#!/usr/bin/env python3

"""
** General GUI tools. **
------------------------
"""

from PyQt6 import QtCore, QtWidgets



class WaitCursor:
    """
    ** Context manager for a wait cursor. **
    """

    def __init__(self, widget: QtWidgets.QWidget):
        assert isinstance(widget, QtWidgets.QWidget), widget.__class__.__name__
        self.widget = widget
        self.old_cursor = None

    def __enter__(self):
        self.old_cursor = self.widget.cursor()
        self.widget.setCursor(QtCore.Qt.CursorShape.WaitCursor)

    def __exit__(self, *_):
        self.widget.setCursor(self.old_cursor)
