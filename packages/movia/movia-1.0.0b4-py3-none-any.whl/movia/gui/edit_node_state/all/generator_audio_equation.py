#!/usr/bin/env python3

"""
** Properties of a ``movia.core.generation.audio.equation.GeneratorAudioEquation``. **
--------------------------------------------------------------------------------------
"""

from PyQt6 import QtWidgets

from movia.core.compilation.sympy_to_torch import _parse_expr
from movia.gui.edit_node_state.base import EditBase



class EditGeneratorAudioEquation(EditBase):
    """
    ** Allows to view and modify the properties of a node of type ``GeneratorAudioEquation``.
    """

    def __init__(self, parent, node_name):
        super().__init__(parent, node_name)

        self.signal_textboxs = self.signal_labels = None

        self.grid_layout = QtWidgets.QGridLayout()
        self.init_signal(self.grid_layout)
        self.setLayout(self.grid_layout)

    def init_signal(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the signals. **
        """
        class _Val:
            def __init__(self, signal_index, window):
                self.signal_index = signal_index
                self.window = window
            def __call__(self, text):
                return self.window.update_signal(text, self.signal_index)
            def __repr__(self): # for remove pylint R0903
                return f"verification limit {self.signal_index}"
        signals = self.state["signals"] + [""]
        self.signal_labels = [
            QtWidgets.QLabel(f"Channel {i} expression:") for i in range(len(signals))
        ]
        self.signal_textboxs = [None for _ in signals]
        for i, signal in enumerate(signals):
            self.signal_textboxs[i] = QtWidgets.QLineEdit()
            self.signal_textboxs[i].setText(str(signal))
            self.signal_textboxs[i].textChanged.connect(_Val(i, self))
            grid_layout.addWidget(self.signal_labels[i], ref_span, 0)
            grid_layout.addWidget(self.signal_textboxs[i], ref_span, 1)
            ref_span += 1
        return ref_span

    def update_signal(self, text, signal_index):
        """
        ** Check that the signal is correct and update all the signals. **
        """
        changed = False
        if not text and signal_index >= 1 and signal_index + 1 == len(self.state["signals"]):
            changed = True
            new_signals = self.state["signals"][:signal_index]
        else:
            try:
                signal = _parse_expr(text)
            except (SyntaxError, ZeroDivisionError):
                self.signal_textboxs[signal_index].setStyleSheet("background:red;")
                return
            if set(map(str, signal.free_symbols)) - {"t"}:
                self.signal_textboxs[signal_index].setStyleSheet("background:red;")
                return
            new_signals = self.state["signals"].copy()
            if signal_index < len(new_signals):
                new_signals[signal_index] = str(signal)
            else:
                changed = True
                new_signals.append(str(signal))
        self.try_set_state(
            self.get_new_state({"signals": new_signals}), self.signal_textboxs[signal_index]
        )
        if changed: # redraw the limits fields
            for widget in self.signal_textboxs + self.signal_labels:
                if widget is not None:
                    widget.deleteLater()
            self.init_signal(self.grid_layout)
