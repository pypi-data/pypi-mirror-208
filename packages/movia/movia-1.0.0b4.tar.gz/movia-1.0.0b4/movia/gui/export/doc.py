#!/usr/bin/env python3

"""
** Processing of ffmpeg documentation. **
-----------------------------------------
"""

import logging

from PyQt6 import QtGui, QtWidgets

from movia.gui.base import MoviaWidget



class DocViewer(MoviaWidget, QtWidgets.QWidget):
    """
    ** Allows to show and hide a documentation. **
    """

    def __init__(self, parent, doc_getter: callable):
        super().__init__(parent)
        self._parent = parent
        self.doc_getter = doc_getter

        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self._doc_label = QtWidgets.QLabel(scroll_area)
        font = QtGui.QFont("", -1)
        font.setFixedPitch(True)
        if not QtGui.QFontInfo(font).fixedPitch():
            logging.warning("no fixed pitch font found")
        self._doc_label.setFont(font)
        scroll_area.setWidget(self._doc_label)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Documentation:", self), 0, 0)
        layout.addWidget(scroll_area, 0, 1)
        self.setLayout(layout)

    def refresh(self):
        """
        ** Update the doc content and displaying. **
        """
        doc_content = self.doc_getter(self)
        self._doc_label.setText(doc_content)
        if doc_content:
            self.show()
        else:
            self.hide()
