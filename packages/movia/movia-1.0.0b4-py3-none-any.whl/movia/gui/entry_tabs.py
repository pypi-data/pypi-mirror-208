#!/usr/bin/env python3

"""
** The widget that contains all the elements to pick from to add them to the timeline. **
-----------------------------------------------------------------------------------------
"""

from PyQt6 import QtWidgets

from movia.gui.base import MoviaWidget
from movia.gui.entry.filters import Filters
from movia.gui.entry.generators import Generators
from movia.gui.entry.project_files import ProjectFiles



class EntryTabs(MoviaWidget, QtWidgets.QWidget):
    """
    ** Contains the different selection windows. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        # declaration
        self.project_files = ProjectFiles(self)
        self.generators = Generators(self)
        self.filters = Filters(self)

        # location
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.project_files, "Project Files")
        tabs.addTab(self.generators, "Generators")
        tabs.addTab(self.filters, "Filters")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def refresh(self):
        """
        ** Updates the elements of this widget and child widgets. **
        """
        self.project_files.refresh()
        self.generators.refresh()
        self.filters.refresh()
