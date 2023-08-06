#!/usr/bin/env python3

"""
** Allows you to select the parameters of an audio stream. **
-------------------------------------------------------------
"""

import logging
import re

from PyQt6 import QtWidgets

from movia.core.compilation.export.rate import _available_audio_rates, suggest_audio_rate
from movia.core.exceptions import IncompatibleSettings
from movia.gui.base import MoviaWidget



CLASSICAL_RATES = {
    8000: "telephone",
    11025: "lower-quality PCM",
    22050: "speech low quality",
    32000: "speech hight quality",
    37800: "cd-rom-xa",
    44056: "ntsc",
    44100: "standard cd-audio, human perception threshold",
    47250: "pcm",
    48000: "standard video",
    50000: "sound-stream",
    50400: "Mitsubishi X-80",
    88200: "pro audio gear uses 2*44100",
    96000: "dvd-audio, bd-rom 2*48000",
    176400: "pro audio gear uses 4*44100",
    192000: "pro audio gear uses 4*48000",
}




class PreferencesAudio(MoviaWidget, QtWidgets.QWidget):
    """
    ** Allows you to select the sampling frequency and the number of channels of an audio stream. **
    """

    def __init__(self, parent, index_abs):
        super().__init__(parent)
        self._parent = parent

        self.locks = set()
        self.rate_textbox = None
        self.rate_combobox = None

        tree = self.app.tree()
        self.stream = tree.in_streams[index_abs]
        self.index_rel = None
        for i, stream in enumerate(tree.in_select("audio")):
            if stream is self.stream:
                self.index_rel = i
        assert self.index_rel is not None, "the output container has been modified in background"

        grid_layout = QtWidgets.QGridLayout()
        self.init_rate(grid_layout)
        self.setLayout(grid_layout)

    def _select_rate(self, text):
        """
        ** From combo box. **
        """
        if "update_combo_box" in self.locks:
            return
        if text == "default":
            self.app.export_settings["rates"]["audio"][self.index_rel] = "default"
            print(f"update rate (stream audio {self.index_rel}): 'default'")
            self.locks.add("no_validate")
            try:
                self.rate_textbox.setText(str(self.rate))
                self.rate_textbox.setStyleSheet("background:none;")
            finally:
                self.locks.discard("no_validate")
        elif text != "manual":
            rate = re.search(r"\d+", text).group()
            self._validate_rate(rate)

    def _validate_rate(self, text):
        """
        ** Check that the frame rate is a correct fraction. **
        """
        if "no_validate" in self.locks:
            return
        self.locks.add("no_validate")
        try:
            # parsing verification
            try:
                rate = int(text)
            except ValueError:
                self.rate_textbox.setStyleSheet("background:red;")
                return
            if rate <= 0:
                self.rate_textbox.setStyleSheet("background:red;")
                return

            # compatibility with codec verification
            encodec = self.app.export_settings["encoders"]["audio"][self.index_rel]
            if encodec == "default":
                encodec = self.app.export_settings["codecs"]["audio"][self.index_rel]
            if encodec != "default":
                try:
                    if choices := _available_audio_rates(encodec):
                        if rate not in choices:
                            raise IncompatibleSettings(
                                f"with the '{encodec}' encodec, "
                                f"the only available sample rates are {sorted(choices)}, "
                                f"but {rate} is specified"
                            )
                except IncompatibleSettings as err:
                    self.rate_textbox.setStyleSheet("background:red;")
                    if "from_refresh" in self.locks:
                        raise err
                    logging.warning(err)
                    return

            # apply changes
            self.app.export_settings["rates"]["audio"][self.index_rel] = rate
            print(f"update rate (stream audio {self.index_rel}): {rate}")
            self.rate_textbox.setText(text)
            self.rate_textbox.setStyleSheet("background:none;")
            self.rate_combobox.setCurrentText("manual")
            self.main_window.refresh()
        finally:
            self.locks.discard("no_validate")

    def init_rate(self, grid_layout, ref_span=0):
        """
        ** Displays and allows to modify the framerate. **
        """
        grid_layout.addWidget(QtWidgets.QLabel("Sample Rate (Hz):"), ref_span, 0)
        self.rate_textbox = QtWidgets.QLineEdit()
        self.rate_textbox.setText(str(self.rate))
        self.rate_textbox.textChanged.connect(self._validate_rate)
        grid_layout.addWidget(self.rate_textbox, ref_span, 1)
        grid_layout.addWidget(QtWidgets.QLabel("Selection:"), ref_span+1, 0)
        self.rate_combobox = QtWidgets.QComboBox()
        self.update_rates_choices()
        self.rate_combobox.currentTextChanged.connect(self._select_rate)
        grid_layout.addWidget(self.rate_combobox, ref_span+1, 1)
        return ref_span + 2

    @property
    def rate(self) -> int:
        """
        ** Get the settings rate. **
        """
        rate = self.app.export_settings["rates"]["audio"][self.index_rel]
        if rate == "default":
            encodec = self.app.export_settings["encoders"]["audio"][self.index_rel]
            if encodec == "default":
                encodec = self.app.export_settings["codecs"]["audio"][self.index_rel]
            rate = suggest_audio_rate(self.stream, encodec)
        return rate

    def refresh(self):
        self.locks.add("from_refresh")
        try:
            self.update_rates_choices()
            if self.app.export_settings["rates"]["audio"][self.index_rel] == "default":
                self._select_rate("default")
            else:
                self._validate_rate(str(self.app.export_settings["rates"]["audio"][self.index_rel]))
        except IncompatibleSettings as err:
            QtWidgets.QMessageBox.warning(None, "Samplerate Conflict", str(err))
        finally:
            self.locks.discard("from_refresh")

    def update_rates_choices(self):
        """
        ** Upddate the combobox with the available options. **
        """
        self.locks.add("update_combo_box")
        try:
            self.rate_combobox.clear()
            self.rate_combobox.addItem("default")
            self.rate_combobox.addItem("manual")
            encodec = self.app.export_settings["encoders"]["audio"][self.index_rel]
            if encodec == "default":
                encodec = self.app.export_settings["codecs"]["audio"][self.index_rel]
            if encodec == "default":
                rates = CLASSICAL_RATES
            else:
                rates = _available_audio_rates(encodec) or CLASSICAL_RATES
            for rate in sorted(rates):
                if rate in CLASSICAL_RATES:
                    self.rate_combobox.addItem(f"{rate} ({CLASSICAL_RATES[rate]})")
                else:
                    self.rate_combobox.addItem(str(rate))
            if self.app.export_settings["rates"]["audio"][self.index_rel] != "default":
                self.rate_combobox.setCurrentText("manual")
        finally:
            self.locks.discard("update_combo_box")
