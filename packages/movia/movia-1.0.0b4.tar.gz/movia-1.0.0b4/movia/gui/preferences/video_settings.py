#!/usr/bin/env python3

"""
** Allows you to select the parameters of a video stream. **
------------------------------------------------------------
"""

from fractions import Fraction
import re

from PyQt6 import QtWidgets

from movia.core.analysis.stream.shape import optimal_shape_video
from movia.core.compilation.export.rate import suggest_video_rate
from movia.gui.base import MoviaWidget



class PreferencesVideo(MoviaWidget, QtWidgets.QWidget):
    """
    ** Allows you to select the frame fps, the resolution and the profile of a video stream. **
    """

    def __init__(self, parent, index_abs):
        super().__init__(parent)
        self._parent = parent

        self.is_processing = False
        self.widgets = {"fpstext": None, "fpscomb": None, "shapetext": None, "shapecomb": None}

        tree = self.app.tree()
        self.stream = tree.in_streams[index_abs]
        self.index_rel = None
        for i, stream in enumerate(tree.in_select("video")):
            if stream is self.stream:
                self.index_rel = i
        assert self.index_rel is not None, "the output container has been modified in background"

        grid_layout = QtWidgets.QGridLayout()
        ref_span = self.init_fps(grid_layout)
        separador = QtWidgets.QFrame()
        separador.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        grid_layout.addWidget(separador, ref_span, 0, 1, 2)
        self.init_shape(grid_layout, ref_span=ref_span+1)
        self.setLayout(grid_layout)

    def _select_fps(self, text):
        """
        ** From fps combo box. **
        """
        if text == "default":
            self.app.export_settings["rates"]["video"][self.index_rel] = "default"
            print(f"update rate (stream video {self.index_rel}): 'default'")
            self.is_processing = True
            self.widgets["fpstext"].setText(str(self.fps))
            self.widgets["fpstext"].setStyleSheet("background:none;")
            self.is_processing = False
            self.main_window.refresh()
        elif text != "manual":
            fps = sorted(re.findall(r"\d+/?\d*", text), key=len)[-1]
            self._validate_fps(fps)

    def _select_shape(self, text):
        """
        ** From shape combo box. **
        """
        if text == "default":
            self.app.export_settings["shapes"][self.index_rel] = "default"
            print(f"update shape (stream video {self.index_rel}): 'default'")
            self.is_processing = True
            self.widgets["shapetext"].setText("x".join(map(str, self.shape[::-1])))
            self.widgets["shapetext"].setStyleSheet("background:none;")
            self.is_processing = False
            self.main_window.refresh()
        elif text == "manual":
            self._validate_shape(self.widgets["shapetext"].text())
        else:
            shape = re.search(r"\d+x\d+", text).group()
            self._validate_shape(shape)

    def _validate_fps(self, text):
        """
        ** Check that the frame fps is a correct fraction. **
        """
        if self.is_processing:
            return
        try:
            fps = Fraction(text)
        except (ValueError, ZeroDivisionError):
            self.widgets["fpstext"].setStyleSheet("background:red;")
            return
        if fps <= 0:
            self.widgets["fpstext"].setStyleSheet("background:red;")
            return
        self.app.export_settings["rates"]["video"][self.index_rel] = str(fps)
        print(f"update rate (stream video {self.index_rel}): '{fps}'")
        self.widgets["fpstext"].setText(text)
        self.widgets["fpstext"].setStyleSheet("background:none;")
        self.widgets["fpscomb"].setCurrentText("manual")
        self.main_window.refresh()

    def _validate_shape(self, text):
        """
        ** Check that the shape is correct. **
        """
        if self.is_processing:
            return
        shape = re.findall(r"\d+", text)
        if len(shape) != 2:
            self.widgets["shapetext"].setStyleSheet("background:red;")
            return
        shape = [int(shape[1]), int(shape[0])]
        if shape[0] <= 0 or shape[1] <= 0:
            self.widgets["shapetext"].setStyleSheet("background:red;")
            return
        self.app.export_settings["shapes"][self.index_rel] = shape
        self.widgets["shapetext"].setText(text)
        self.widgets["shapetext"].setStyleSheet("background:none;")
        self.widgets["shapecomb"].setCurrentText("manual")
        self.main_window.refresh()

    def init_fps(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the framerate. **
        """
        grid_layout.addWidget(QtWidgets.QLabel("Frame Rate (fps):"), ref_span, 0)
        self.widgets["fpstext"] = QtWidgets.QLineEdit()
        self.widgets["fpstext"].setText(str(self.fps))
        self.widgets["fpstext"].textChanged.connect(self._validate_fps)
        grid_layout.addWidget(self.widgets["fpstext"], ref_span, 1)
        grid_layout.addWidget(QtWidgets.QLabel("Selection:"), ref_span+1, 0)
        self.widgets["fpscomb"] = QtWidgets.QComboBox()
        self.widgets["fpscomb"].addItems([
            "default", "manual",
            "15 (animation)",
            "23.98 = 24000/1001 (old cinema)",
            "24 (old cinema)",
            "25 (old television)",
            "29.97 (30000/1001 standard)",
            "30",
            "50",
            "59.94 (60000/1001 modern television)",
            "60",
            "120 (human perception threshold)",
            "240 (slow-motion)",
            "300 (slow-motion)",
        ])
        if self.app.export_settings["rates"]["video"][self.index_rel] != "default":
            self.widgets["fpscomb"].setCurrentText("manual")
        self.widgets["fpscomb"].currentTextChanged.connect(self._select_fps)
        grid_layout.addWidget(self.widgets["fpscomb"], ref_span+1, 1)
        return ref_span + 2

    def init_shape(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the shape of the frames. **
        """
        grid_layout.addWidget(QtWidgets.QLabel("Resolution (width x height):"), ref_span, 0)
        self.widgets["shapetext"] = QtWidgets.QLineEdit()
        self.widgets["shapetext"].setText("x".join(map(str, self.shape[::-1]))) # h*w to w*h
        self.widgets["shapetext"].textChanged.connect(self._validate_shape)
        grid_layout.addWidget(self.widgets["shapetext"], ref_span, 1)
        grid_layout.addWidget(QtWidgets.QLabel("Selection:"), ref_span+1, 0)
        self.widgets["shapecomb"] = QtWidgets.QComboBox()
        self.widgets["shapecomb"].addItems([
            "default", "manual",
            "426x240 16:9 (240p)",
            "640x360 16:9 (360p)",
            "854x480 16:9 (480p)",
            "1280x720 16:9 (720p HD High Definition)",
            "1920x1080 16:9 (1080p FHD Full HD)",
            "2560x1440 16:9 (1440p QHD Quad HD)",
            "3840x2160 16:9 (4K UHD Ultra HD)",
            "7680x4320 16:9 (8K Full Ultra HD)",
        ])
        if self.app.export_settings["shapes"][self.index_rel] != "default":
            self.widgets["shapecomb"].setCurrentText("manual")
        self.widgets["shapecomb"].currentTextChanged.connect(self._select_shape)
        grid_layout.addWidget(self.widgets["shapecomb"], ref_span+1, 1)
        return ref_span + 2

    @property
    def fps(self) -> Fraction:
        """
        ** Get the settings fps. **
        """
        fps = self.app.export_settings["rates"]["video"][self.index_rel]
        if fps == "default":
            fps = suggest_video_rate(self.stream)
        else:
            fps = Fraction(fps)
        return fps

    @property
    def shape(self):
        """
        ** Get the settings shape. **
        """
        shape = self.app.export_settings["shapes"][self.index_rel]
        if shape == "default":
            shape = optimal_shape_video(self.stream) or [1080, 1920]
        return shape
