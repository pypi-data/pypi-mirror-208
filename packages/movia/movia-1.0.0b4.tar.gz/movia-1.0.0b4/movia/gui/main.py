#!/usr/bin/env python3

"""
** Entry point of the graphic interface. **
-------------------------------------------
"""

import json
import pathlib
import typing

from PyQt6 import QtCore, QtWidgets

from movia.gui.actions import create_actions
from movia.gui.app.app import App
from movia.gui.base import MoviaWidget
from movia.gui.edition_tabs import EditionTabs
from movia.gui.entry_tabs import EntryTabs
from movia.gui.export.main import WindowsExportSettings
from movia.gui.menu import fill_menu
from movia.gui.preferences.main import PreferencesTabs
from movia.gui.toolbar import MainToolBar
from movia.gui.tools import WaitCursor
from movia.gui.video_preview.main import VideoPreview



class MainWindow(MoviaWidget, QtWidgets.QMainWindow):
    """
    ** The main window for video editing interface. **
    """

    def __init__(self):
        super().__init__()
        self._parent = None

        self._app = App()

        self.actions = create_actions(self)

        # declaration
        self.setWindowTitle("Movia")
        self.sub_windows = {
            "toolbar": MainToolBar(self, self.actions),
            "entry_tabs": EntryTabs(self),
            "video_preview": VideoPreview(self),
            "edition_tabs": EditionTabs(self),
        }
        fill_menu(self.menuBar(), self.actions)

        # location
        self.addToolBar(self.sub_windows["toolbar"])
        h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        h_splitter.addWidget(self.sub_windows["entry_tabs"])
        h_splitter.addWidget(self.sub_windows["video_preview"])
        v_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self)
        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(self.sub_windows["edition_tabs"])
        self.setCentralWidget(v_splitter)

    @property
    def app(self):
        """
        ** Allows to rewrite this method of the parent class. **
        """
        return self._app

    def closeEvent(self, event):
        """
        ** Takes precautions before properly releasing resources. **
        """
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle("Unregistered changes")
        box.setText("Do you want to save before closing?")
        box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard
        )
        box.setIcon(QtWidgets.QMessageBox.Icon.Question)
        button = box.exec()
        if button == QtWidgets.QMessageBox.StandardButton.Save:
            self.save()
        event.accept()

    def crash(self, msg):
        """
        ** Displays a critical error message. **
        """
        QtWidgets.QMessageBox.critical(None, "Application crashed", msg)

    def export(self):
        """
        ** Brings up the export window. **
        """
        WindowsExportSettings(self).exec()

    def import_files(self):
        """
        ** Append files to the project. **
        """
        new_files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Import Multimedia Files")
        files = self.app.project_files # copy is implicitely done
        files.extend(new_files)
        try:
            self.app.project_files = files
        except AssertionError as err:
            QtWidgets.QMessageBox.warning(
                None, "Invalid files", f"Unable to append the files {files} : {err}"
            )
        self.sub_windows["entry_tabs"].refresh()

    def open(self, file: typing.Union[None, str, pathlib.Path]=None):
        """
        ** Load a new project file. **

        Parameters
        ----------
        project_file : pathlike, optional
            The name or path of the file. If not provide, a dialog file explorateur windows pop.
        """
        if file is None:
            file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open", filter="*.json")
            if not file:
                return
        assert isinstance(file, (str, pathlib.Path)), file.__class__.__name__
        with open(file, "r", encoding="utf8") as raw:
            state = json.load(raw)
        self.app.__setstate__(state)
        self.app.set_save_file(file)
        self.refresh()

    def preferences(self):
        """
        ** Displays the preferences window. **
        """
        PreferencesTabs(self).exec()

    def refresh(self):
        """
        ** Updates the elements of this widget and child widgets. **
        """
        with WaitCursor(self):
            self.sub_windows["entry_tabs"].refresh()
            self.sub_windows["video_preview"].refresh()
            self.sub_windows["edition_tabs"].refresh()

    def save(self):
        """
        ** Save all the state in a file, nn        . **
        """
        if self.app.get_save_file() is None:
            self.save_as()
            return
        with open(self.app.get_save_file(), "w", encoding="utf8") as file:
            json.dump(self.app.__getstate__(), file, check_circular=False, indent=4, sort_keys=True)

    def save_as(self):
        """
        ** Set a new recording file and invoque save. **
        """
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Project", filter="*.json")
        if not file:
            return
        file = pathlib.Path(file)
        file = file.with_suffix(".json")
        self.app.set_save_file(file)
        self.save()
