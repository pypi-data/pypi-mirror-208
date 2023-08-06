#!/usr/bin/env python3

"""
** Allows you to choose a format and codecs. **
-----------------------------------------------

The information collected here concerns the encoding and not the decoding.
"""

import itertools
import multiprocessing.pool
import os
import re
import subprocess
import typing

import numpy as np

from movia.core.optimisation.cache.singleton import MetaSingleton



def _check_encoder_compatibility(encodec_muxer_kind: tuple[str, str, str]) -> bool:
    """
    ** Pickable version for chec an encoder / codec compatibility with a specific muxer. **
    """
    encodec, muxer, kind = encodec_muxer_kind
    if kind == "video":
        cmd = [
            "timeout", "30", "ffmpeg", "-v", "error", "-y",
            "-f", "rawvideo", "-r", "24", "-pix_fmt", "yuv420p", "-s", "32x32", "-i", "pipe:",
            "-c:v", encodec, "-strict", "experimental", "-f", muxer, os.devnull,
        ]
        data = os.urandom(7680) # 32 pxl * 32 pxl * 12 bits / pxl * 5 frames
    elif kind == "audio":
        cmd = [
            "timeout", "30", "ffmpeg", "-v", "error", "-y",
            "-f", "s8", "-ar", "48000", "-ac", "2", "-i", "pipe:",
            "-c:a", encodec, "-strict", "experimental", "-f", muxer, os.devnull,
        ]
        data = os.urandom(9600) # 2 channels * 100 ms
    elif kind == "subtitle":
        cmd = [
            "timeout", "30", "ffmpeg", "-v", "error", "-y",
            "-f", "srt", "-i", "pipe:",
            "-c:s", encodec, "-strict", "experimental", "-f", muxer, os.devnull,
        ]
        data = b"1\n00:00:00-->00:00:01\nthis is subtitle" # str format
    else:
        return False
    try:
        subprocess.run(cmd, input=data, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    return True


class WriteInfos(metaclass=MetaSingleton):
    """
    ** Extract informations about codecs, encoders and muxers. **
    """

    def __init__(self):
        self.codecs_cache = WriteInfos.codecs_init()
        self.encoders_cache = WriteInfos.encoders_init()
        self.muxers_cache = WriteInfos.muxers_init()
        self._compatibilites = {} # all tested combinaisons of (encodec, format) -> is_compatible

    def check_compatibilities(
        self, encodecs: list[str], muxers: list[str]
    ) -> np.ndarray[bool]:
        """
        ** Asynchronously checks codec combinations. **

        Parameters
        ----------
        encodecs : list[str]
            The codec or encoder names.
        muxers : list[str]
            The muxer (format) names.

        Returns
        -------
        compatibility_matrix : np.ndarray[bool]
            The 2d boolean compatibility matrix.
            Item (i, j) is True if encodecs[i] is compatible with muxers[j].

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> WriteInfos().check_compatibilities(["h264", "libx265", "opus"], ["matroska", "ogg"])
        array([[ True, False],
               [ True, False],
               [ True,  True]])
        >>> WriteInfos().check_compatibilities([], [])
        array([], shape=(1, 0), dtype=bool)
        >>> WriteInfos().check_compatibilities(["opus"], [])
        array([], shape=(1, 0), dtype=bool)
        >>> WriteInfos().check_compatibilities([], ["ogg"])
        array([], shape=(1, 0), dtype=bool)
        >>>
        """
        assert isinstance(encodecs, list), encodecs.__class__.__name__
        assert all(isinstance(ec, str) for ec in encodecs), encodecs
        assert set(encodecs).issubset(self.codecs|self.encoders), \
            set(encodecs)-(self.codecs|self.encoders)
        assert isinstance(muxers, list), muxers.__class__.__name__
        assert all(isinstance(f, str) for f in muxers), muxers
        assert set(muxers).issubset(self.muxers), set(muxers)-self.muxers

        # case empty:
        if len(encodecs) == 0 or len(muxers) == 0:
            return np.asarray([[]], dtype=bool) # oblige for keep 2d array homogeneous

        # makes checks
        if (ecs_ms := [
            ec_m for ec_m in itertools.product(encodecs, muxers) if ec_m not in self._compatibilites
        ]): # only for optimisation
            encodecs_cache = {**self.codecs_cache, **self.encoders_cache}
            with multiprocessing.pool.ThreadPool() as pool: # subprocess release the GIL
                for encodec_and_muxer, is_compatible in zip(
                    ecs_ms,
                    pool.imap(
                        _check_encoder_compatibility,
                        ((ec, f, encodecs_cache[ec]["type"]) for ec, f in ecs_ms)
                    )
                ):
                    self._compatibilites[encodec_and_muxer] = is_compatible

        # create matrix
        return np.asarray(
            [
                [self._compatibilites[(encodec, muxer)] for muxer in muxers]
                for encodec in encodecs
            ],
            dtype=bool,
        )

    @property
    def codecs(self) -> set[str]:
        """
        ** Returns all eligible codecs. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> codecs = WriteInfos().codecs
        >>> "av1" in codecs
        True
        >>> "vorbis" in codecs
        True
        >>> "subrip" in codecs
        True
        >>>
        """
        return set(self.codecs_cache)

    @staticmethod
    def codecs_init() -> dict[str, dict[str]]:
        """
        ** Parse ``ffmpeg -codecs``. **
        """
        codecs = {}
        doc = subprocess.run(
            ("ffmpeg", "-v", "error", "-codecs"), capture_output=True, check=True
        ).stdout.decode()
        general_pattern = (
            r"(?P<decoding_supported>[D. ])"
            r"(?P<encoding_supported>E)" # catch writer only
            r"(?P<type>[VAS. ])"
            r"(?P<intra_frame_only_codec>[I. ])"
            r"(?P<lossly_compression>[L. ])"
            r"(?P<lossless_compression>[S. ])"
            r"\s+(?P<codec>[a-z0-9_\-]{2,})\s+"
            r"(?P<long_name>\S.*\S)"
        )
        encoders_pattern = r"\(encoders:\s(?P<encoders>([a-z0-9_\-]{2,}\s)+)\)"
        for line in doc.split("\n"):
            if (match := re.search(general_pattern, line)) is not None:
                match_encoders = re.search(encoders_pattern, line)
                if match_encoders is not None:
                    encoders = set(match_encoders["encoders"].split())
                else:
                    encoders = {match["codec"]}
                codecs[match["codec"]] = {
                    "decoding_supported": (match["decoding_supported"] == "D"),
                    "encoding_supported": (match["encoding_supported"] == "E"),
                    "type": {"V": "video", "A": "audio", "S": "subtitle"}.get(match["type"], None),
                    "intra_frame_only_codec": (match["intra_frame_only_codec"] == "I"),
                    "lossly_compression": (match["lossly_compression"] == "L"),
                    "lossless_compression": (match["lossless_compression"] == "S"),
                    "long_name": match["long_name"],
                    "encoders": encoders,
                }
        return codecs

    @property
    def encoders(self) -> set[str]:
        """
        ** Returns all eligible encoders. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> encoders = WriteInfos().encoders
        >>> "libaom-av1" in encoders
        True
        >>> "libvorbis" in encoders
        True
        >>> "srt" in encoders
        True
        >>>
        """
        return set(self.encoders_cache)

    @staticmethod
    def encoders_init() -> dict[str, dict[str]]:
        """
        ** Parse ``ffmpeg -encoders``. **
        """
        encoders = {}
        doc = subprocess.run(
            ("ffmpeg", "-v", "error", "-encoders"), capture_output=True, check=True,
        ).stdout.decode()
        general_pattern = (
            r"(?P<type>[VAS. ])"
            r"(?P<frame_level_multithreading>[F. ])"
            r"(?P<slice_level_multithreading>[S. ])"
            r"(?P<experimental>[X. ])"
            r"(?P<supports_draw_horiz_band>[B. ])"
            r"(?P<supports_direct_rendering_method>[D. ])"
            r"\s+(?P<encoder>[a-z0-9_\-]{2,})\s+"
            r"(?P<long_name>\S.*\S)"
        )
        codec_pattern = r"\(codec\s(?P<codec>[a-z0-9_\-]{2,})\)"
        for line in doc.split("\n"):
            if (match := re.search(general_pattern, line)) is not None:
                match_codec = re.search(codec_pattern, line)
                if match_codec is not None:
                    codec = match_codec["codec"]
                else:
                    codec = match["encoder"]
                encoders[match["encoder"]] = {
                    "type": {"V": "video", "A": "audio", "S": "subtitle"}.get(match["type"], None),
                    "frame_level_multithreading": (match["frame_level_multithreading"] == "F"),
                    "slice_level_multithreading": (match["slice_level_multithreading"] == "S"),
                    "experimental": (match["experimental"] == "X"),
                    "supports_draw_horiz_band": (match["supports_draw_horiz_band"] == "B"),
                    "supports_direct_rendering_method": (
                        match["supports_direct_rendering_method"] == "D"
                    ),
                    "long_name": match["long_name"],
                    "codec": codec,
                }
        return encoders

    def get_codecs_for_muxer(self, muxer: str) -> set[str]:
        """
        ** Search all available codecs for a given muxer. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> sorted(WriteInfos().get_codecs_for_muxer("ogg"))
        ['flac', 'opus', 'speex', 'theora', 'vorbis', 'vp8']
        >>>
        """
        assert isinstance(muxer, str), muxer.__class__.__name__
        assert muxer in self.muxers, f"{muxer} not in {self.muxers}"

        if "codecs" not in self.muxers_cache[muxer]:
            all_codecs = list(self.codecs)
            mask = self.check_compatibilities(all_codecs, [muxer])[:, 0]
            codecs = set(np.asarray(all_codecs, dtype=object)[mask])
            self.muxers_cache[muxer]["codecs"] = codecs
        return self.muxers_cache[muxer]["codecs"]

    def get_encoder_doc(self, encoder: str) -> str:
        r"""
        ** Retrive the ffmpeg documentation of this encoder. **
        """
        assert isinstance(encoder, str), encoder.__class__.__name__
        assert encoder in self.encoders, f"{encoder} not in {self.encoders}"

        if self.encoders_cache[encoder].get("doc") is None:
            self.encoders_cache[encoder]["doc"] = subprocess.run(
                ["ffmpeg", "-v", "error", "-h", f"encoder={encoder}"],
                capture_output=True, check=True,
            ).stdout.decode()
        return self.encoders_cache[encoder]["doc"]

    def get_encoders_for_muxer(self, muxer: str) -> set[str]:
        """
        ** Search all available encoders for a given muxer. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> sorted(WriteInfos().get_encoders_for_muxer("ogg"))
        ['flac', 'libopus', 'libspeex', 'libtheora', 'libvorbis', 'libvpx', 'opus', 'vorbis']
        >>>
        """
        assert isinstance(muxer, str), muxer.__class__.__name__
        assert muxer in self.muxers, f"{muxer} not in {self.muxers}"

        if "encoders" not in self.muxers_cache[muxer]:
            all_encoders = [
                encoder for codec in self.get_codecs_for_muxer(muxer)
                for encoder in CodecInfos(codec).encoders
            ] # more optimised than list(self.encoders)
            mask = self.check_compatibilities(all_encoders, [muxer])[:, 0]
            encoders = set(np.asarray(all_encoders, dtype=object)[mask])
            self.muxers_cache[muxer]["encoders"] = encoders
        return self.muxers_cache[muxer]["encoders"]

    def get_muxer_doc(self, muxer: str) -> str:
        r"""
        ** Retrive the ffmpeg documentation of this format. **
        """
        assert isinstance(muxer, str), muxer.__class__.__name__
        assert muxer in self.muxers, f"{muxer} not in {self.muxers}"

        doc = self.muxers_cache[muxer].get("doc") or subprocess.run(
            ["ffmpeg", "-v", "error", "-h", f"muxer={muxer}"],
            capture_output=True, check=True,
        ).stdout.decode()
        self.muxers_cache[muxer]["doc"] = doc
        return doc

    def get_muxers_for_codec(self, codec: str) -> set[str]:
        """
        ** Search all available codecs for a given format. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> sorted(WriteInfos().get_muxers_for_codec("av1")) # doctest +ELLIPSIS
        ['asf', 'asf_stream', 'avi', ..., 'vob', 'webm', 'wtv']
        >>>
        """
        assert isinstance(codec, str), codec.__class__.__name__
        assert codec in self.codecs, f"{codec} not in {self.codecs}"

        all_muxers = list(self.muxers)
        mask = self.check_compatibilities([codec], all_muxers)[0, :]
        muxers = set(np.asarray(all_muxers, dtype=object)[mask])
        self.codecs_cache[codec]["muxers"] = muxers
        return muxers

    @property
    def muxers(self) -> set[str]:
        """
        ** Returns all eligible muxers. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import WriteInfos
        >>> muxers = WriteInfos().muxers
        >>> "ogg" in muxers
        True
        >>> "matroska" in muxers
        True
        >>>
        """
        return set(self.muxers_cache)

    @staticmethod
    def muxers_init() -> dict[str, dict[str]]:
        """
        ** Parse ``ffmpeg -muxers``. **
        """
        muxers = {}
        doc = subprocess.run(
            ("ffmpeg", "-v", "error", "-muxers"), capture_output=True, check=True,
        ).stdout.decode()
        pattern = (
            r"[D. ]E"
            r"\s+(?P<muxer>[a-zA-Z0-9_\-]{2,})\s+"
            r"(?P<long_name>\S.*\S)"
        )
        for line in doc.split("\n"):
            if (match := re.search(pattern, line)) is not None:
                muxers[match["muxer"]] = {
                    "long_name": match["long_name"],
                }
        for special in (
            "alsa", "audiotoolbox", "caca", "decklink", "fbdev", "image2pipe", "null", "opengl",
            "oss", "pulse", "rtp", "sdl", "xv",
        ):
            if special in muxers: # remove some special muxers
                del muxers[special]
        return muxers


class CodecInfos(metaclass=MetaSingleton):
    """
    ** All informations for a specific codec. **
    """

    def __init__(self, name: str):
        assert isinstance(name, str), name.__class__.__name__
        self.infos = WriteInfos()
        assert name in self.infos.codecs, f"{name} not in {self.infos.codecs}"
        self.name = name

    @property
    def encoders(self) -> set[str]:
        """
        ** The alvailable encoders for this codec. **

        Notes
        -----
        No real tests are performed, it is just a documentation parsing.

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import CodecInfos
        >>> sorted(CodecInfos("opus").encoders)
        ['libopus', 'opus']
        >>>
        """
        return self.infos.codecs_cache[self.name]["encoders"]

    @property
    def decoding_supported(self):
        """
        ** Returns True if the codec is able to read. **
        """
        return self.infos.codecs_cache[self.name]["decoding_supported"]

    @property
    def encoding_supported(self):
        """
        ** Returns True if the codec is able to write. **
        """
        return self.infos.codecs_cache[self.name]["encoding_supported"]

    def get_all(self) -> dict:
        """
        ** Get the complete dictionary. **
        """
        return {
            "encoding_supported": self.encoding_supported,
            "decoding_supported": self.decoding_supported,
            "intra_frame_only_codec": self.intra_frame_only_codec,
            "long_name": self.long_name,
            "lossless_compression": self.lossless_compression,
            "lossly_compression": self.lossly_compression,
            "type": self.type,
        }

    @property
    def intra_frame_only_codec(self):
        """
        ** Returns True if the codec is intra-frame only. **
        """
        return self.infos.codecs_cache[self.name]["intra_frame_only_codec"]

    @property
    def long_name(self) -> str:
        """
        ** The complete verbose long name of the encoder. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import CodecInfos
        >>> CodecInfos("aac").long_name
        'AAC (Advanced Audio Coding) (decoders: aac aac_fixed )'
        >>>
        """
        return self.infos.codecs_cache[self.name]["long_name"]

    @property
    def lossless_compression(self):
        """
        ** Returns True if the codec is able to keep all information. **
        """
        return self.infos.codecs_cache[self.name]["lossless_compression"]

    @property
    def lossly_compression(self):
        """
        ** Returns True if the codec is able to compress. **
        """
        return self.infos.codecs_cache[self.name]["lossly_compression"]

    @property
    def type(self) -> str:
        """
        ** The kind of encodable flux video, audio or subtitle. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import CodecInfos
        >>> CodecInfos("av1").type
        'video'
        >>> CodecInfos("vorbis").type
        'audio'
        >>> CodecInfos("subrip").type
        'subtitle'
        >>>
        """
        return self.infos.codecs_cache[self.name]["type"]


class EncoderInfos(metaclass=MetaSingleton):
    """
    ** All informations for a specific encoder. **
    """

    def __init__(self, name: str):
        assert isinstance(name, str), name.__class__.__name__
        self.infos = WriteInfos()
        assert name in self.infos.encoders, f"{name} not in {self.infos.encoders}"
        self.name = name

    @property
    def codec(self) -> str:
        """
        ** The name of the codec associated to this encoder. **

        Notes
        -----
        No real tests are performed, it is just a documentation parsing.

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import EncoderInfos
        >>> EncoderInfos("libaom-av1").codec
        'av1'
        >>>
        """
        return self.infos.encoders_cache[self.name]["codec"]

    @property
    def doc(self) -> str:
        """
        ** The ffmpeg documentation about this encoder. **
        """
        return self.infos.get_encoder_doc(self.name)

    @property
    def experimental(self) -> bool:
        """
        ** True if the encoder is experimental. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import EncoderInfos
        >>> EncoderInfos("libx264").experimental
        False
        >>>
        """
        return self.infos.encoders_cache[self.name]["experimental"]

    @property
    def frame_level_multithreading(self) -> bool:
        """
        ** True if the codec accepts frame level multithreading. **
        """
        return self.infos.encoders_cache[self.name]["frame_level_multithreading"]

    def get_all(self) -> dict:
        """
        ** Get the complete dictionary. **
        """
        return {
            "doc": self.doc,
            "experimental": self.experimental,
            "frame_level_multithreading": self.frame_level_multithreading,
            "long_name": self.long_name,
            "rates": self.rates,
            "slice_level_multithreading": self.slice_level_multithreading,
            "supports_direct_rendering_method": self.supports_direct_rendering_method,
            "supports_draw_horiz_band": self.supports_draw_horiz_band,
            "type": self.type,
        }

    @property
    def long_name(self) -> str:
        """
        ** The complete verbose long name of the encoder. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import EncoderInfos
        >>> EncoderInfos("aac").long_name
        'AAC (Advanced Audio Coding)'
        >>>
        """
        return self.infos.encoders_cache[self.name]["long_name"]

    @property
    def rates(self) -> set[int]:
        """
        ** The audio compatible sample rates. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import EncoderInfos
        >>> sorted(EncoderInfos("libopus").rates)
        [8000, 12000, 16000, 24000, 48000]
        >>>
        """
        if (match := re.search(r"sample rates: (?P<rates>(?:\d+\s)+)", self.doc)) is None:
            return set()
        return set(map(int, match["rates"].split()))

    @property
    def slice_level_multithreading(self) -> bool:
        """
        ** True if the encoder accepts slice level multithreading. **
        """
        return self.infos.encoders_cache[self.name]["slice_level_multithreading"]

    @property
    def supports_draw_horiz_band(self) -> bool:
        """
        ** True if the encoder supports draw horizontal band. **
        """
        return self.infos.encoders_cache[self.name]["supports_draw_horiz_band"]

    @property
    def supports_direct_rendering_method(self) -> bool:
        """
        ** True if the encoder supports direct rendering method. **
        """
        return self.infos.encoders_cache[self.name]["supports_direct_rendering_method"]

    @property
    def type(self) -> str:
        """
        ** The kind of encodable flux video, audio or subtitle. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import EncoderInfos
        >>> EncoderInfos("libaom-av1").type
        'video'
        >>> EncoderInfos("libopus").type
        'audio'
        >>> EncoderInfos("srt").type
        'subtitle'
        >>>
        """
        return self.infos.encoders_cache[self.name]["type"]


class MuxerInfos(metaclass=MetaSingleton):
    """
    ** All informations for a specific muxer (writting container). **
    """

    def __init__(self, name: str):
        assert isinstance(name, str), name.__class__.__name__
        self.infos = WriteInfos()
        assert name in self.infos.muxers, f"{name} not in {self.infos.muxers}"
        self.name = name

    @property
    def codecs(self) -> set[str]:
        """
        ** Tests all codecs to find the compatibles. **
        """
        return self.infos.get_codecs_for_muxer(self.name)

    def contains_encodecs(self, encodecs: typing.Iterable[str]) -> bool:
        """
        ** Returns True if this muxer support all the given codecs. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import MuxerInfos
        >>> MuxerInfos("ogg").contains_encodecs(["theora", "vorbis"])
        True
        >>> MuxerInfos("ogg").contains_encodecs(["h264"])
        False
        >>>
        """
        assert hasattr(encodecs, "__iter__"), encodecs.__class__.__name__
        encodecs = list(encodecs)
        assert all(isinstance(e, str) for e in encodecs), encodecs
        assert set(encodecs).issubset(self.infos.codecs|self.infos.encoders), \
            set(encodecs)-(self.infos.codecs|self.infos.encoders)
        return self.infos.check_compatibilities(encodecs, [self.name]).all()

    @property
    def default_codecs(self) -> dict[str, str]:
        """
        ** Extract the default codecs from the documentation. **

        Notes
        -----
        No real tests are performed, it is just a documentation parsing.

        Examples
        --------
        >>> from pprint import pprint
        >>> from movia.core.compilation.export.compatibility import MuxerInfos
        >>> pprint(MuxerInfos("matroska").default_codecs)
        {'audio': 'vorbis', 'subtitle': 'ass', 'video': 'h264'}
        >>>
        """
        pattern = r"Default (?P<type>audio|video|subtitle) codec: (?P<codec>[a-z0-9_\-]{2,})\."
        default = {
            match["type"]: match["codec"] for match in re.finditer(pattern, self.doc)
            if match["codec"] in self.infos.codecs
        }
        if not default:
            return {}
        codecs = list(default.values())
        codecs_rank = {c: i for i, c in enumerate(codecs)}
        codecs_ok = self.infos.check_compatibilities(codecs, [self.name])[:, 0]
        default = {t: c for t, c in default.items() if codecs_ok[codecs_rank[c]]}
        return default

    @property
    def doc(self) -> str:
        """
        ** The ffmpeg documentation about this codec. **
        """
        return self.infos.get_muxer_doc(self.name)

    @property
    def encoders(self) -> set[str]:
        """
        ** Tests all encoders to find the compatibles. **
        """
        return self.infos.get_encoders_for_muxer(self.name)

    @property
    def extensions(self) -> set[str]:
        """
        ** Get all suffixs for this format. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import MuxerInfos
        >>> MuxerInfos("matroska").extensions
        {'.mkv'}
        >>> sorted(MuxerInfos("mpeg").extensions)
        ['.mpeg', '.mpg']
        >>>

        Notes
        -----
        The returns set can be empty.
        """
        pattern = r"Common extensions: (?P<exts>(?:[a-z0-9]{2,},?)+)\."
        if (match := re.search(pattern, self.doc)) is None:
            return set()
        exts = {f".{ext}" for ext in match["exts"].split(",")}
        return exts

    @classmethod
    def from_suffix(cls, suffix: str):
        """
        ** Create the muxer info instance from the conventional given filename extension. **

        Parameters
        ----------
        suffix : str
            The extension in upper or lower case, including the ".".

        Raises
        ------
        KeyError
            If the extension is not associate to any muxer.

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import MuxerInfos
        >>> MuxerInfos.from_suffix(".mkv").name
        'matroska'
        >>>
        """
        assert isinstance(suffix, str), suffix.__class__.__name__

        # get all avalaible extensions
        all_suffix = {}
        for muxer in WriteInfos().muxers:
            for suf in MuxerInfos(muxer).extensions:
                all_suffix[suf] = all_suffix.get(suf, set())
                all_suffix[suf].add(muxer)

        # simple case
        if suffix.lower() not in all_suffix:
            raise KeyError(f"{suffix} not in {sorted(all_suffix)}")
        muxers = all_suffix[suffix.lower()]
        if len(muxers) == 1:
            return cls(muxers.pop())

        # if we have to choose
        muxers = [cls(name) for name in muxers]

        # 1 choice, if one of the muxer supports only this extension
        if len(criteria := [m for m in muxers if m.extensions == {suffix}]) == 1:
            return criteria.pop()
        if len(criteria) > 0:
            muxers = criteria

        # 2 choice, the variety of available type.
        cost = {"audio": 2, "video": 4, "subtitle": 1}
        best = max(criteria := [{cost[CodecInfos(c).type] for c in m.codecs} for m in muxers])
        if len(criteria := [m for m, cost in zip(muxers, criteria) if cost == best]) == 1:
            return criteria.pop()
        muxers = criteria

        # 3 choice, the number of available codecs
        best = max(criteria := [len(m.codecs) for m in muxers])
        if len(criteria := [m for m, cost in zip(muxers, criteria) if cost == best]) == 1:
            return criteria.pop()
        muxers = criteria

        # 4 choice, the lenght of the documentation
        best = max(criteria := [len(m.doc) for m in muxers])
        if len(criteria := [m for m, cost in zip(muxers, criteria) if cost == best]) == 1:
            return criteria.pop()

        raise NotImplementedError(f"no more criteria for choose {criteria} for {suffix}")

    def get_all(self) -> dict[str]:
        """
        ** Get the complete dictionary. **
        """
        return {
            "codecs": self.codecs,
            "default_codecs": self.default_codecs,
            "doc": self.doc,
            "extensions": self.extensions,
            "long_name": self.long_name,
        }

    @property
    def long_name(self) -> str:
        """
        ** The complete verbose long name of the codec. **

        Examples
        --------
        >>> from movia.core.compilation.export.compatibility import MuxerInfos
        >>> MuxerInfos("avi").long_name
        'AVI (Audio Video Interleaved)'
        >>>
        """
        return self.infos.muxers_cache[self.name]["long_name"]
