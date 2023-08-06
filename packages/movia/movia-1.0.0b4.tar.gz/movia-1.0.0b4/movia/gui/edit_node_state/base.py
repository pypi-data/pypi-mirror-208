#!/usr/bin/env python3

"""
** Allows you to unify all node editing windows. **
---------------------------------------------------

Defines several accessors that allow to lighten the code of child classes.
"""

from PyQt6 import QtWidgets

from movia.gui.base import MoviaWidget



class EditBase(MoviaWidget, QtWidgets.QWidget):
    """
    ** Common base class for all node editing classes. **
    """

    def __init__(self, parent, node_name):
        super().__init__(parent)
        self._parent = parent
        assert node_name in self.app.graph.nodes, (node_name, set(self.app.graph.nodes))
        self.node_name = node_name
        self.ref = [] # for keeping the reference of the interfaces

    def get_new_state(self, changes: dict[str]) -> dict[str]:
        """
        ** Returns a copy of the old state with the new attribute. **
        """
        return {k: changes.get(k, o) for k, o in self.state.items()}

    def get_class(self) -> type:
        """
        ** Returns the node class. **
        """
        return self.app.graph.nodes[self.node_name]["class"]

    @property
    def state(self) -> dict[str]:
        """
        ** Returns a pointer of the node state. **
        """
        return self.app.graph.nodes[self.node_name]["state"]

    def try_set_state(self, new_state: dict[str], textbox=None) -> bool:
        """
        ** If possible, try to apply the change to the node. **

        In case of AssertionError, the changes are not applied
        and a popup window appears to display the error message.

        Parameters
        ----------
        new_state : dict
            The new different state.
        textbox : PyQt6.QWidget, optional
            Must accepts the method setStyleSheet for changing the bakground color.

        Returns
        -------
        failed : boolean
            False if succes and True if AssertionError raise in check.
        """
        old_state = self.state.copy()
        assert set(new_state) == set(old_state), (new_state, old_state)

        # search and format differences
        changes = {k: (o, new_state[k]) for k, o in old_state.items() if o != new_state[k]}
        changes_str = "\n".join(f"change {k} from {o} to {n}" for k, (o, n) in changes.items())

        # apply changes
        self.app.graph.nodes[self.node_name]["state"] = new_state
        try:
            self.app.tree_node(self.node_name)
            self.main_window.refresh() # maybe can cause indirect errors
        except AssertionError as err:
            self.app.graph.nodes[self.node_name]["state"] = old_state
            if textbox is not None:
                textbox.setStyleSheet("background:red;")
            QtWidgets.QMessageBox.warning(
                None,
                f"Invalid state of {self.node_name}",
                f"{changes_str}\n\n{err}"
            )
            return True
        if textbox is not None:
            textbox.setStyleSheet("background:none;")
        print(changes_str)
        return False
