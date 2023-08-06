#!/usr/bin/env python3

"""
** Interactive window for help to choose the export settings. **
----------------------------------------------------------------
"""

from fractions import Fraction
import ast
import pathlib
import stat

import black
from PyQt6 import QtWidgets

from movia.core.compilation.export.default import suggest_export_params
from movia.core.compilation.graph_to_ast import graph_to_ast
from movia.core.compilation.tree_to_graph import tree_to_graph
from movia.core.exceptions import IncompatibleSettings
from movia.core.io.write import ContainerOutputFFMPEG
from movia.gui.base import MoviaWidget
from movia.gui.export.container import ContainerSettings
from movia.gui.export.encodec import EncoderSettings
from movia.gui.tools import WaitCursor



class WindowsExportSettings(MoviaWidget, QtWidgets.QDialog):
    """
    ** Show the exportation settings. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        with WaitCursor(self.main_window):
            self._container_settings = ContainerSettings(self)
            self._encoders = [
                EncoderSettings(self, stream) for stream in self.app.tree().in_streams
            ]

            self.setWindowTitle("Export settings")

            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self._container_settings)
            for encoder in self._encoders:
                separador = QtWidgets.QFrame()
                separador.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                layout.addWidget(separador)
                layout.addWidget(encoder)
            self.init_next(layout)
            self.setLayout(layout)

            self.refresh()

    def export(self):
        """
        ** Compile to python, close main windows and excecute the new file. **
        """
        self.accept()
        streams = self.app.tree().in_streams

        # conversion of supplied parameters
        filename = (
            pathlib.Path(self.app.export_settings["parent"]) / self.app.export_settings["stem"]
        )

        indexs = {}
        streams_settings = []
        for stream in streams:
            index = indexs.get(stream.type, -1) + 1
            indexs[stream.type] = index
            streams_settings.append({
                "encodec": self.app.export_settings["codecs"][stream.type][index],
                "option": self.app.export_settings["encoders_settings"][stream.type][index],
            })
            if streams_settings[-1]["encodec"] == "default":
                streams_settings[-1]["encoders"] = (
                    self.app.export_settings["encoders"][stream.type][index]
                )
            if stream.type == "audio":
                streams_settings[-1]["rate"] = (
                    self.app.export_settings["rates"]["audio"][index] or "default"
                )
            elif stream.type == "video":
                streams_settings[-1]["rate"] = (
                    Fraction(self.app.export_settings["rates"]["video"][index]) or "default"
                )
                streams_settings[-1]["shape"] = (
                    self.app.export_settings["shapes"][index] or "default"
                )
            else:
                raise TypeError(f"not yet supported {stream.type}")

        container_settings = {
            "format": self.app.export_settings["muxer"],
            "container_options": self.app.export_settings["muxer_settings"],
        }

        # completes the missing parameters
        try:
            filename, streams_settings, container_settings = suggest_export_params(
                streams,
                filename=filename,
                streams_settings=streams_settings,
                container_settings=container_settings,
            )
        except IncompatibleSettings as err:
            QtWidgets.QMessageBox.warning(None, "Incompatible Parameters", str(err))

        # compilation to executable code
        tree = ContainerOutputFFMPEG(
            streams,
            filename=filename,
            streams_settings=streams_settings,
            container_settings=container_settings,
        )
        code = ast.unparse(graph_to_ast(tree_to_graph(tree)))
        code = "#!/usr/bin/env python3\n\n" + code
        code = black.format_str(code, mode=black.Mode())

        # write file and give execution permission
        filename = filename.with_suffix(".py")
        with open(filename, "w", encoding="utf-8") as code_file:
            code_file.write(code)
        filename.chmod(filename.stat().st_mode | stat.S_IEXEC)

        # close
        self.main_window.close()

    def init_next(self, layout):
        """
        ** The button for the next stape. **
        """
        separador = QtWidgets.QFrame()
        separador.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        layout.addWidget(separador)
        button = QtWidgets.QPushButton("Let's Go!")
        button.clicked.connect(self.export)
        layout.addWidget(button)

    def refresh(self):
        with WaitCursor(self):
            self._container_settings.refresh()
            for enc in self._encoders:
                enc.refresh()
