#!/usr/bin/env python3

"""
** Interactive window for a specific edge properties. **
--------------------------------------------------------
"""

import math

from PyQt6 import QtCore, QtWidgets

from movia.gui.base import MoviaWidget
from movia.gui.edit_node_state.main import EditNodeWindow



class WindowEdgeProperties(MoviaWidget, QtWidgets.QDialog):
    """
    ** Show the edge properties. **
    """

    def __init__(self, parent, edge_name):
        super().__init__(parent)
        self._parent = parent
        self.edge_name = edge_name

        grid_layout = QtWidgets.QGridLayout()
        self.setWindowTitle("Stream Informations")

        # the main properties
        ref_span = self.init_properties(grid_layout)

        # add a separator
        separador = QtWidgets.QFrame()
        separador.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        grid_layout.addWidget(separador, ref_span, 0, 1, 2)
        ref_span += 1

        # add basic properties of pointed nodes
        ref_span = self.init_context(grid_layout, ref_span=ref_span)

        # access to the procreator node
        self.init_procreator(grid_layout, ref_span=ref_span)

        self.setLayout(grid_layout)

    def init_context(self, grid_layout, ref_span=0):
        """
        ** Add the information about the in and out node. **
        """
        in_index, out_index = self.edge_name[2].split("->")
        title = QtWidgets.QLabel("Nodes Context")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        grid_layout.addWidget(title, ref_span, 0, 1, 2)
        grid_layout.addWidget(QtWidgets.QLabel("Source Node Name:"), ref_span+1, 0)
        grid_layout.addWidget(QtWidgets.QLabel(self.edge_name[0]), ref_span+1, 1)
        grid_layout.addWidget(QtWidgets.QLabel("Source Node Stream:"), ref_span+2, 0)
        grid_layout.addWidget(QtWidgets.QLabel(f"out stream {in_index}"), ref_span+2, 1)
        grid_layout.addWidget(QtWidgets.QLabel("Destination Node Name:"), ref_span+3, 0)
        grid_layout.addWidget(QtWidgets.QLabel(self.edge_name[1]), ref_span+3, 1)
        grid_layout.addWidget(QtWidgets.QLabel("Destination Node Stream:"), ref_span+4, 0)
        grid_layout.addWidget(QtWidgets.QLabel(f"in stream {out_index}"), ref_span+4, 1)
        return ref_span + 5

    def init_procreator(self, grid_layout, ref_span=0):
        """
        ** Allows to access the properties of the parent node. **
        """
        button = QtWidgets.QPushButton()
        button.setText("Parent Node Properties")
        button.clicked.connect(self.open_procreator)
        grid_layout.addWidget(button, ref_span, 0, 1, 2)
        return ref_span + 1

    def init_properties(self, grid_layout, ref_span=0):
        """
        ** Add the informations about the stream properties. **
        """
        stream = self.app.tree_edge(self.edge_name)

        # the title of the section
        title = QtWidgets.QLabel("Stream Properties")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        grid_layout.addWidget(title, ref_span, 0, 1, 2)
        ref_span += 1

        # the general type
        grid_layout.addWidget(QtWidgets.QLabel("Type:"), ref_span, 0)
        grid_layout.addWidget(QtWidgets.QLabel(stream.type.title()), ref_span, 1)
        ref_span += 1

        # all ancestors
        ancestors = " <-- ".join(c.__name__ for c in stream.__class__.__mro__[-2::-1])
        grid_layout.addWidget(QtWidgets.QLabel("Ancestors:"), ref_span, 0)
        grid_layout.addWidget(QtWidgets.QLabel(ancestors), ref_span, 1)
        ref_span += 1

        # beginning
        beginning = float(stream.beginning)
        if beginning == math.inf:
            beginning = "infinite"
        else:
            beginning = (
                f"{round(beginning//3600):0>2}:{round(beginning%3600//60):0>2}:{beginning%60:.3f} "
                f"({stream.beginning} seconds)"
            )
        grid_layout.addWidget(QtWidgets.QLabel("Beginning:"), ref_span, 0)
        grid_layout.addWidget(QtWidgets.QLabel(beginning), ref_span, 1)
        ref_span += 1

        # duration
        duration = float(stream.duration)
        if duration == math.inf:
            duration = "infinite"
        else:
            duration = (
                f"{round(duration//3600):0>2}:{round(duration%3600//60):0>2}:{duration%60:.3f} "
                f"({stream.duration} seconds)"
            )
        grid_layout.addWidget(QtWidgets.QLabel("Duration:"), ref_span, 0)
        grid_layout.addWidget(QtWidgets.QLabel(duration), ref_span, 1)
        ref_span += 1

        # time continuous
        continuous = {True: "yes", False: "no"}[stream.is_time_continuous]
        grid_layout.addWidget(QtWidgets.QLabel("Time is continuous:"), ref_span, 0)
        grid_layout.addWidget(QtWidgets.QLabel(continuous), ref_span, 1)
        ref_span += 1

        # space continuous
        if stream.type == "video":
            continuous = {True: "yes", False: "no"}[stream.is_space_continuous]
            grid_layout.addWidget(QtWidgets.QLabel("Space is continuous:"), ref_span, 0)
            grid_layout.addWidget(QtWidgets.QLabel(continuous), ref_span, 1)
            ref_span += 1

        # channels
        if stream.type == "audio":
            grid_layout.addWidget(QtWidgets.QLabel("Channels:"), ref_span, 0)
            grid_layout.addWidget(QtWidgets.QLabel(str(stream.channels)), ref_span, 1)
            ref_span += 1

        return ref_span

    def open_procreator(self):
        """
        ** Created and opens the property window for the parent node. **
        """
        EditNodeWindow(self, self.edge_name[0]).exec()
