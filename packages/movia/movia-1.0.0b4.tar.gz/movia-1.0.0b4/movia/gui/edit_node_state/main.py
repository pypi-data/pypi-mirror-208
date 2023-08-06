#!/usr/bin/env python3

"""
** Global and contextual window for viewing and editing the properties of a node. **
------------------------------------------------------------------------------------
"""

from PyQt6 import QtCore, QtWidgets

from movia.gui.base import MoviaWidget
from movia.gui.edit_node_state.documentation import Documentation
from movia.gui.edit_node_state.general import General
from movia.gui.edit_node_state.loader import load_edit_windows



class EditNodeWindow(MoviaWidget, QtWidgets.QDialog):
    """
    ** Show the node properties. **
    """

    def __init__(self, parent, node_name):
        super().__init__(parent)
        self._parent = parent
        assert node_name in self.app.graph.nodes, (node_name, set(self.app.graph.nodes))
        self.node_name = node_name

        self._edit_state = None

        self.setWindowTitle(f'Edit node "{node_name}"')

        layout = QtWidgets.QVBoxLayout()
        self.init_general(layout)
        self.init_edit(layout)
        self.init_documentation(layout)
        self.setLayout(layout)

    def init_documentation(self, layout):
        """
        ** Append documentation context. **
        """
        title = QtWidgets.QLabel("Documentation")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        layout.addWidget(title)
        scrollable_layout = QtWidgets.QScrollArea(self)
        scrollable_layout.setWidget(Documentation(self, self.node_name))
        layout.addWidget(scrollable_layout)

    def init_edit(self, layout):
        """
        ** Choose and instantiate the right widget for this node's class. **
        """
        title = QtWidgets.QLabel("Node State")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        layout.addWidget(title)
        edit_class = load_edit_windows(self.app.graph.nodes[self.node_name]["class"])
        self._edit_state = edit_class(self, self.node_name)
        layout.addWidget(self._edit_state)

    def init_general(self, layout):
        """
        ** Append general information context. **
        """
        title = QtWidgets.QLabel("General Node Properties")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        layout.addWidget(title)
        layout.addWidget(General(self, self.node_name))

    def refresh(self):
        self._edit_state.refresh()
