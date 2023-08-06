#!/usr/bin/env python3

"""
** Properties of a ``movia.core.generation.video.equation.GeneratorVideoEquation``. **
--------------------------------------------------------------------------------------
"""

from PyQt6 import QtWidgets

from movia.core.compilation.sympy_to_torch import _parse_expr
from movia.gui.edit_node_state.base import EditBase



class EditGeneratorVideoEquation(EditBase):
    """
    ** Allows to view and modify the properties of a node of type ``GeneratorVideoEquation``.
    """

    def __init__(self, parent, node_name):
        super().__init__(parent, node_name)
        self.color_textboxs = self.color_labels = None

        self.grid_layout = QtWidgets.QGridLayout()
        self.init_expr(self.grid_layout)
        self.setLayout(self.grid_layout)

    def init_expr(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the equations. **
        """
        colors = (
            ("Gray",),
            ("Gray", "Alpha"),
            ("Blue", "Green", "Red"),
            ("Blue", "Green", "Red", "Alpha"),
            ("",)
        )
        exprs = (tuple(map(str, self.state["colors"])) + ("",))[:4]
        colors = (colors[len(exprs)-2] + ("-".join(colors[len(exprs)-1]),))[:len(exprs)]
        vals = (
            (lambda t: self.update_color(t, 0)),
            (lambda t: self.update_color(t, 1)),
            (lambda t: self.update_color(t, 2)),
            (lambda t: self.update_color(t, 3)),
        )[:len(exprs)]
        self.color_textboxs = [None, None, None, None]
        self.color_labels = [None, None, None, None]
        for i, (color, expr, val) in enumerate(zip(colors, exprs, vals)):
            self.color_labels[i] = QtWidgets.QLabel(f"{color} Expression:")
            self.color_textboxs[i] = QtWidgets.QLineEdit()
            self.color_textboxs[i].setText(expr)
            self.color_textboxs[i].textChanged.connect(val)
            grid_layout.addWidget(self.color_labels[i], ref_span, 0)
            grid_layout.addWidget(self.color_textboxs[i], ref_span, 1)
            ref_span += 1
        return ref_span

    def update_color(self, text, color_index):
        """
        ** Check that the formula is correct and update the color. **
        """
        changed = False
        if not text and color_index >= 1 and color_index + 1 == len(self.state["colors"]):
            changed = True
            new_colors = self.state["colors"][:color_index]
        else:
            try:
                color = _parse_expr(text)
            except (SyntaxError, ZeroDivisionError):
                self.color_textboxs[color_index].setStyleSheet("background:red;")
                return
            if set(map(str, color.free_symbols)) - {"i", "j", "t"}:
                self.color_textboxs[color_index].setStyleSheet("background:red;")
                return
            new_colors = self.state["colors"].copy()
            if color_index < len(new_colors):
                new_colors[color_index] = str(color)
            else:
                changed = True
                new_colors.append(str(color))
        self.try_set_state(
            self.get_new_state({"colors": new_colors}), self.color_textboxs[color_index]
        )
        if changed: # redraw the colors fields
            for widget in self.color_textboxs + self.color_labels:
                if widget is not None:
                    widget.deleteLater()
            self.init_expr(self.grid_layout, ref_span=self.ref_span)
