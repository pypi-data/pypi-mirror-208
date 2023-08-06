#!/usr/bin/env python3

"""
** Interactive widget for help to choose the export muxer settings. **
----------------------------------------------------------------------
"""

import multiprocessing.pool
import pathlib

from PyQt6 import QtCore, QtWidgets

from movia.core.compilation.export.compatibility import MuxerInfos, WriteInfos
from movia.gui.base import MoviaWidget
from movia.gui.export._helper import ComboBox
from movia.gui.export.doc import DocViewer
from movia.gui.tools import WaitCursor



class MuxerComboBox(ComboBox):
    """
    ** Lists the availables muxers. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._muxers_cache = None

    def _text_changed(self, name):
        if self.app.export_settings["muxer"] != name:
            with WaitCursor(self.parent.parent):
                self.app.export_settings["muxer"] = name
                print(f"update muxer: {self.app.export_settings['muxer']}")
                if name != "default":
                    suffix = sorted(MuxerInfos(name).extensions)
                    suffix = suffix.pop(0) if len(suffix) >= 1 else ""
                else:
                    suffix = ""
                if self.app.export_settings["suffix"] != suffix:
                    self.app.export_settings["suffix"] = suffix
                    print(f"update export suffix: {self.app.export_settings['suffix']}")
                self.parent.parent.refresh() # WindowsExportSettings

    def available_muxers(self):
        """
        ** Set of muxers supporting the different types of streams, for a given codecs set. **
        """
        codecs_types = (
            (
                (
                    set(self.app.export_settings["codecs"]["audio"])
                    | set(self.app.export_settings["codecs"]["video"])
                ) - {"default"}
            ),
            {stream.type for stream in self.app.tree().in_streams},
        )
        if self._muxers_cache is None or self._muxers_cache[0] != codecs_types:
            muxers = list(WriteInfos().muxers) # frozen the iteration order
            with multiprocessing.pool.ThreadPool() as pool:
                self._muxers_cache = (
                    codecs_types,
                    {
                        muxer for muxer, ok in zip(
                            muxers,
                            pool.imap(
                                (lambda muxer: (
                                    codecs_types[1].issubset(set(MuxerInfos(muxer).default_codecs))
                                    and MuxerInfos(muxer).contains_encodecs(codecs_types[0]))
                                ),
                                muxers
                            )
                        ) if ok
                    },
                )
        return self._muxers_cache[1]

    def refresh(self):
        """
        ** Updates the list with the available muxers. **
        """
        self.clear()
        self.addItem(self.app.export_settings["muxer"])
        for muxer in ["default"] + sorted(self.available_muxers()):
            if muxer == self.app.export_settings["muxer"]:
                continue
            self.addItem(muxer) # QtGui.QIcon.fromTheme("video-x-generic")


class FileNameSelector(MoviaWidget, QtWidgets.QWidget):
    """
    ** File manager for select the filename. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        self._textbox = QtWidgets.QLineEdit(self)
        self._textbox.textChanged.connect(self._validate_path)

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self._textbox, 0, 0)
        button = QtWidgets.QPushButton("Select", self)
        button.clicked.connect(self.filename_dialog)
        grid_layout.addWidget(button, 0, 1)
        self.setLayout(grid_layout)

    def _validate_path(self, new_path):
        """
        ** Try to validate the new path if it is valid. **
        """
        try:
            self.update_path(new_path)
        except AssertionError:
            self._textbox.setStyleSheet("background:red;")
        else:
            self._textbox.setStyleSheet("background:none;")

    def filename_dialog(self):
        """
        ** Opens a window to choose a new file name. **
        """
        new_path, _ = QtWidgets.QFileDialog.getSaveFileName(self)
        if new_path:
            try:
                self.update_path(new_path)
            except AssertionError as err:
                QtWidgets.QMessageBox.warning(
                    None, "Invalid filename", f"Unable to change the filename {new_path} : {err}"
                )

    def update_path(self, new_path):
        """
        ** Check that the new path is correct and set the new path in the settings. **
        """
        with WaitCursor(self.parent.parent):
            assert isinstance(new_path, str), new_path.__class__.__name__
            new_path = pathlib.Path(new_path)
            assert not new_path.is_dir(), new_path
            assert new_path.parent.is_dir(), new_path
            assert new_path.suffix == "" or any(
                new_path.suffix == suf
                for mux in self.parent.muxer_combo_box.available_muxers()
                for suf in MuxerInfos(mux).extensions
            ), f"suffix {new_path.suffix} not allow"

            modif = False

            if self.app.export_settings["parent"] != str(new_path.parent):
                modif = True
                self.app.export_settings["parent"] = str(new_path.parent)
                print(f"update directory: {self.app.export_settings['parent']}")
            if self.app.export_settings["stem"] != new_path.stem:
                modif = True
                self.app.export_settings["stem"] = new_path.stem
                print(f"update file stem: {self.app.export_settings['stem']}")
            if new_path.suffix != self.app.export_settings["suffix"]:
                modif = True
                self.app.export_settings["suffix"] = new_path.suffix
                print(f"update suffix: {self.app.export_settings['suffix']}")
                if new_path.suffix:
                    self.app.export_settings["muxer"] = MuxerInfos.from_suffix(new_path.suffix).name
                    print(f"update muxer: {self.app.export_settings['muxer']}")

            if modif:
                self.parent.parent.refresh() # WindowsExportSettings

    def refresh(self):
        """
        ** Updates the displayed path. **
        """
        new_text = (
            f"{self.app.export_settings['parent']}/{self.app.export_settings['stem']}"
            f"{self.app.export_settings['suffix']}"
        )
        self._textbox.setStyleSheet("background:none;")
        self._textbox.setText(new_text)


class ContainerSettings(MoviaWidget, QtWidgets.QWidget):
    """
    ** Settings of the container file. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        self.filename_selector = FileNameSelector(self)
        self.muxer_combo_box = MuxerComboBox(self)
        self.muxer_doc_viewer = DocViewer(
            self,
            lambda w: (
                "" if (muxer := w.app.export_settings["muxer"]) == "default"
                else MuxerInfos(muxer).doc
            )
        )
        self.muxer_doc_viewer.hide()

        layout = QtWidgets.QGridLayout()
        self.init_title(layout)
        layout.addWidget(QtWidgets.QLabel("Path:", self), 1, 0)
        layout.addWidget(self.filename_selector, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Muxer:", self), 2, 0)
        layout.addWidget(self.muxer_combo_box, 2, 1)
        layout.addWidget(self.muxer_doc_viewer, 3, 0, 1, 2)
        self.setLayout(layout)

    def init_title(self, layout):
        """
        ** The section title. **
        """
        title = QtWidgets.QLabel("Muxer Settings")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        layout.addWidget(title, 0, 0, 1, 2)

    def refresh(self):
        self.filename_selector.refresh()
        self.muxer_combo_box.refresh()
        self.muxer_doc_viewer.refresh()
