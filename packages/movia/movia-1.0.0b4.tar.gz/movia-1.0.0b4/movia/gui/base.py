#!/usr/bin/env python3

"""
** Allows to unify widgets by giving them interesting common properties. **
---------------------------------------------------------------------------
"""



class MoviaWidget:
    """
    ** Allows to unify widgets by giving them interesting common properties. **
    """

    @property
    def app(self):
        """
        ** from movia.gui.base import MoviaWidget. **
        """
        return self.main_window.app

    @property
    def main_window(self):
        """
        ** Get the mother window of this descendant widget. **
        """
        ancestor = self
        ultimate_ancestor = self.parent
        while ultimate_ancestor is not None:
            ancestor, ultimate_ancestor = ultimate_ancestor, ultimate_ancestor.parent
        if not isinstance(ancestor, MoviaWidget):
            raise TypeError(
                f"all ancestors of {self.__class__.__name__} must inherit from ``MoviaWidget``"
            )
        return ancestor

    @property
    def parent(self):
        """
        ** Return the mother window. **
        """
        if (parent := getattr(self, "_parent", None)) is not None:
            if not isinstance(parent, MoviaWidget):
                raise TypeError(f"{parent.__class__.__name__} must inherit from ``MoviaWidget``")
        return parent

    def refresh(self):
        """
        ** Updates this widget and all child widgets. **

        This method can be re-implemented.
        """
        childs = (
            child for attr, child in self.__dict__.items()
            if not attr.startswith("__")
            and child is not self.parent
            and isinstance(child, MoviaWidget)
        )
        for child in childs:
            child.refresh()
