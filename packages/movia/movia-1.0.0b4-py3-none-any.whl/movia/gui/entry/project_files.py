#!/usr/bin/env python3

"""
** Allows to view and copy/drop new files. **
---------------------------------------------
"""

import inspect
import logging
import pathlib

import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets

from movia.core.analysis.ffprobe import get_streams_type
from movia.core.io.read import ContainerInputFFMPEG
from movia.gui.entry.base import Entry



class ProjectFiles(Entry):
    """
    ** Imported files visualization window. **
    """

    def __init__(self, parent):
        super().__init__(parent, [], set(), ())

        self._item2index = {}

        self.itemDoubleClicked.connect(
            lambda item: QtWidgets.QMessageBox.information(
                self, "Info", f"click on project files {item.text()} inactive"
            )
        )

    def dragMoveEvent(self, event):
        """
        ** Need to be defined for calling ``dropEvent``.
        """

    def dragLeaveEvent(self, event):
        """
        ** Prepares for drop in other widgets.
        """
        super().dragLeaveEvent(event)
        if len(self.selectedItems()) == 1:
            file = [i.data(4) for i in self.selectedItems()].pop()
            self.app.global_vars["drag_an_drop"][1]["state"]["filename"] = file

    def dragEnterEvent(self, event):
        """
        ** Drag and drop selection. **
        """
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.accept() # for invoke dragLeaveEvent
            return
        if not event.mimeData().hasFormat("text/plain"):
            event.ignore()
            return
        if not event.mimeData().hasUrls():
            logging.error("drag-and-drop failed (no text)")
            event.ignore()
            return
        for url in event.mimeData().urls():
            url_str = url.toString()
            if not url_str.startswith("file:"):
                logging.error("drag-and-drop failed (not file %s)", url_str)
                event.ignore()
                return
            path = pathlib.Path(url_str[5:])
            if not path.is_file():
                logging.error("drag-and-drop failed (not file exists %s)", path)
                event.ignore()
                return
            if not get_streams_type(path, ignore_errors=True):
                logging.error("drag-and-drop failed (not multimedia stream %s)", path)
                event.ignore()
                return
        event.accept()

    def dropEvent(self, event):
        """
        ** Drag and drop management. **
        """
        for url in event.mimeData().urls():
            url_str = url.toString()
            path = pathlib.Path(url_str[5:])
            self.app.project_files = self.app.project_files + [str(path)]
        self.refresh()

    def keyPressEvent(self, event):
        """
        ** Delete a file. **
        """
        if event.key() == QtCore.Qt.Key.Key_Delete:
            for item in self.selectedItems():
                index = self._item2index[item.text()]
                del self.app.project_files[index]
            self.refresh()

    def refresh(self):
        """
        ** Updates the display of the list. **
        """
        self.clear()
        self._item2index = {}
        for index, file in enumerate(self.app.project_files):
            img = np.zeros((128, 128, 3), dtype=np.uint8)
            icon = QtGui.QIcon(QtGui.QPixmap(QtGui.QImage(
                img.data, img.shape[1], img.shape[0], 3*img.shape[1],
                QtGui.QImage.Format.Format_BGR888
            )))
            item = QtWidgets.QListWidgetItem(icon, pathlib.Path(file).name, parent=self)
            item.setData(
                3,
                (
                    ContainerInputFFMPEG.__name__,
                    pathlib.Path(inspect.getsourcefile(ContainerInputFFMPEG)).resolve(),
                ),
            ) # 0 for text, 1 for icon, 2 for text, 3 is free!
            item.setData(4, file)
            self.addItem(item)
            self._item2index[item.text()] = index
