#!/usr/bin/env python3

"""
** Interactive widget for help to choose the export codecs/encoders settings. **
--------------------------------------------------------------------------------
"""

from PyQt6 import QtCore, QtWidgets

from movia.core.compilation.export.compatibility import (CodecInfos, EncoderInfos, MuxerInfos,
    WriteInfos)
from movia.gui.base import MoviaWidget
from movia.gui.export._helper import ComboBox
from movia.gui.export.doc import DocViewer
from movia.gui.preferences.audio_settings import PreferencesAudio
from movia.gui.preferences.video_settings import PreferencesVideo



class CodecComboBox(ComboBox):
    """
    ** Lists the availables codecs. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._codecs_cache = None

    def _text_changed(self, name):
        index = self.parent.index
        stream_type = self.parent.stream.type
        if self.app.export_settings["codecs"][stream_type][index] != name:
            self.app.export_settings["codecs"][stream_type][index] = name
            print(f"update codec (stream {stream_type} {index}): {name}")
            self.parent.encoder_combo_box.text_changed("default")
            self.parent.parent.refresh() # WindowsExportSettings

    def available_codecs(self):
        """
        ** Set of codecs supporting for this streams. **

        Takes in account the muxer and the stream type.
        """
        muxer = self.app.export_settings["muxer"]
        if self._codecs_cache is None or self._codecs_cache[0] != muxer:
            if muxer == "default":
                codecs = WriteInfos().codecs
            else:
                codecs = MuxerInfos(muxer).codecs
            stream_type = self.parent.stream.type
            codecs = {codec for codec in codecs if CodecInfos(codec).type == stream_type}
            self._codecs_cache = (muxer, codecs)
        return self._codecs_cache[1]

    def refresh(self):
        """
        ** Updates the list with the available codecs. **
        """
        self.clear()
        codec = self.app.export_settings["codecs"][self.parent.stream.type][self.parent.index]
        if codec != "default" and codec not in self.available_codecs():
            self.text_changed("default")
            return
        self.addItem(codec)
        for codec_ in ["default"] + sorted(self.available_codecs()):
            if codec_ == codec:
                continue
            self.addItem(codec_)


class EncoderComboBox(ComboBox):
    """
    ** Lists the availables encoders. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._encoders_cache = None

    def _text_changed(self, name):
        index = self.parent.index
        stream_type = self.parent.stream.type
        if self.app.export_settings["encoders"][stream_type][index] != name:
            self.app.export_settings["encoders"][stream_type][index] = name
            print(f"update encoder (stream {stream_type} {index}): {name}")
            self.parent.parent.refresh() # WindowsExportSettings

    def available_encoders(self):
        """
        ** Set of encoders supporting for this streams. **

        Takes in account the codec. Trys the real compatibility with the muxer.
        """
        codec = self.app.export_settings["codecs"][self.parent.stream.type][self.parent.index]
        muxer = self.app.export_settings["muxer"]
        if self._encoders_cache is None or self._encoders_cache[0] != (codec, muxer):
            if codec == "default":
                encoders = set()
            else:
                encoders = CodecInfos(codec).encoders
            if muxer != "default":
                encoders = list(encoders) # frozen the iteration order
                encoders = {
                    e for e, ok in zip(
                        encoders, WriteInfos().check_compatibilities(encoders, [muxer]).ravel()
                    ) if ok
                }
            self._encoders_cache = ((codec, muxer), encoders)
        return self._encoders_cache[1]

    def refresh(self):
        """
        ** Updates the list with the available encoders. **
        """
        self.clear()
        encoder = self.app.export_settings["encoders"][self.parent.stream.type][self.parent.index]
        if encoder != "default" and encoder not in self.available_encoders():
            self.text_changed("default")
            return
        self.addItem(encoder)
        for encoder_ in ["default"] + sorted(self.available_encoders()):
            if encoder_ == encoder:
                continue
            self.addItem(encoder_)


class EncoderSettings(MoviaWidget, QtWidgets.QWidget):
    """
    ** Able to choose and edit the encoder for a given stream. **
    """

    def __init__(self, parent, stream):
        super().__init__(parent)
        self._parent = parent
        self.stream = stream

        self.preset = None
        self.codec_combo_box = CodecComboBox(self)
        self.encoder_label = QtWidgets.QLabel("Encoder:", self)
        self.encoder_label.hide()
        self.encoder_combo_box = EncoderComboBox(self)
        self.encoder_combo_box.hide()
        self.encoder_doc_viewer = DocViewer(
            self,
            lambda doc_viewer: (
                "" if (
                    encoder := (
                        doc_viewer.app.export_settings
                    )["encoders"][self.stream.type][doc_viewer.parent.index]
                ) == "default" else EncoderInfos(encoder).doc
            )
        )
        self.encoder_doc_viewer.hide()

        grid_layout = QtWidgets.QGridLayout()
        ref_span = self.init_title(grid_layout)
        ref_span = self.init_preset(grid_layout, ref_span)
        grid_layout.addWidget(QtWidgets.QLabel("Codec:"), ref_span+1, 0)
        grid_layout.addWidget(self.codec_combo_box, ref_span+1, 1)
        grid_layout.addWidget(self.encoder_label, ref_span+2, 0)
        grid_layout.addWidget(self.encoder_combo_box, ref_span+2, 1)
        grid_layout.addWidget(self.encoder_doc_viewer, ref_span+3, 0, 1, 2)
        self.setLayout(grid_layout)

    @property
    def index(self):
        """
        ** The input stream relative index of the container output. **
        """
        for index, stream in enumerate(self.app.tree().in_select(self.stream.type)):
            if stream is self.stream:
                return index
        raise KeyError(f"the stream {self.stream} is missing in the container output")

    @property
    def index_abs(self):
        """
        ** The input stream absolute index of the container output. **
        """
        for index, stream in enumerate(self.app.tree().in_streams):
            if stream is self.stream:
                return index
        raise KeyError(f"the stream {self.stream} is missing in the container output")

    def init_preset(self, grid_layout, ref_span=0):
        """
        ** The preferences. **
        """
        grid_layout.addWidget(QtWidgets.QLabel("Profile:"), ref_span, 0)
        if self.stream.type == "audio":
            self.preset = PreferencesAudio(self, self.index_abs)
        elif self.stream.type == "video":
            self.preset = PreferencesVideo(self, self.index_abs)
        else:
            raise NotImplementedError(f"not yet supported {self.stream.type}")
        grid_layout.addWidget(self.preset, ref_span, 1)
        return ref_span + 1

    def init_title(self, grid_layout, ref_span=0):
        """
        ** The section title. **
        """
        title = QtWidgets.QLabel(
            f"Stream {self.index_abs} {self.stream.type} {self.index} Settings"
        )
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold")
        grid_layout.addWidget(title, ref_span, 0, 1, 2)
        return ref_span + 1

    def refresh(self):
        self.codec_combo_box.refresh()
        self.encoder_combo_box.refresh()
        if self.app.export_settings["codecs"][self.stream.type][self.index] == "default":
            self.encoder_label.hide()
            self.encoder_combo_box.hide()
        else:
            self.encoder_label.show()
            self.encoder_combo_box.show()
        self.encoder_doc_viewer.refresh()
        self.preset.refresh()
