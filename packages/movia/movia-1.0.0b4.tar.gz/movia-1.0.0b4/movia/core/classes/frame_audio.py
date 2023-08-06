#!/usr/bin/env python3

"""
** Defines the structure an audio frame. **
-------------------------------------------
"""

from fractions import Fraction
import numbers
import re
import typing

import torch

from movia.core.classes.frame import Frame



class FrameAudio(Frame):
    """
    ** An audio sample packet with time information. **

    Behaves like a torch tensor of shape (nbr_channels, samples).
    The shape is consistent with pyav and torchaudio.
    Values are supposed to be between -1 and 1.

    Parameters
    ----------
    channels : int
        The numbers of channels (readonly).
    rate : int
        The frequency of the samples in Hz (readonly).
    samples : int
        The number of samples per channels (readonly).
    time : Fraction
        The time of the first sample of the frame in second (readonly).
    """

    def __new__(cls,
        time: typing.Union[Fraction, int], rate: numbers.Integral, *args, **kwargs
    ):
        frame = super().__new__(cls, *args, metadata=[time, rate], **kwargs)
        frame.check_state()
        return frame

    def __repr__(self) -> str:
        """
        ** Allows to add metadata to the display. **

        Examples
        --------
        >>> from fractions import Fraction
        >>> import torch
        >>> from movia.core.classes.frame_audio import FrameAudio
        >>>
        >>> FrameAudio(Fraction(1, 2), 48000, torch.zeros((2, 1024)))
        FrameAudio(Fraction(1, 2), 48000, [[0. 0. 0. ... 0. 0. 0.]
                                           [0. 0. 0. ... 0. 0. 0.]])
        >>> _.to(dtype=torch.float16)
        FrameAudio(Fraction(1, 2), 48000, [[0. 0. 0. ... 0. 0. 0.]
                                           [0. 0. 0. ... 0. 0. 0.]],
                                          dtype=torch.float16)
        >>> _.requires_grad = True
        >>> _
        FrameAudio(Fraction(1, 2), 48000, [[0. 0. 0. ... 0. 0. 0.]
                                           [0. 0. 0. ... 0. 0. 0.]],
                                          dtype=torch.float16,
                                          requires_grad=True)
        >>>
        """
        tensor_str = str(self.numpy(force=True))
        header = f"{self.__class__.__name__}({repr(self.time)}, {self.rate}, "
        tensor_str = ("\n" + " "*len(header)).join(tensor_str.split("\n"))
        if (infos := re.findall(r"\w+=[a-zA-Z0-9_\-.\"']+", torch.Tensor.__repr__(self))):
            infos = "\n" + " "*len(header) + (",\n" + " "*len(header)).join(infos)
            return f"{header}{tensor_str},{infos})"
        return f"{header}{tensor_str})"

    @property
    def channels(self) -> int:
        """
        ** The numbers of channels. **

        Examples
        --------
        >>> from movia.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, 2, 10).channels
        2
        >>>
        """
        return self.shape[0]

    def check_state(self) -> None:
        """
        ** Apply verifications. **

        Raises
        ------
        AssertionError
            If something wrong in this frame.
        """
        assert isinstance(self.metadata[0], (Fraction, int)), \
            self.metadata[0].__class__.__name__ # corresponds to time attribute
        self.metadata[0] = Fraction(self.metadata[0])
        assert isinstance(self.metadata[1], numbers.Integral), \
            self.metadata[1].__class__.__name__ # corresponds to rate attribute
        self.metadata[1] = int(self.metadata[1])
        assert self.metadata[1] > 0, self.metadata[1] # corresponds to rate attribute
        assert self.ndim == 2, self.shape
        assert self.shape[0] > 0, self.shape # nbr_channels
        assert self.dtype.is_floating_point, self.dtype

    @property
    def rate(self) -> int:
        """
        ** The frequency of the samples in Hz. **

        Examples
        --------
        >>> from movia.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, 2, 1024).rate
        48000
        >>>
        """
        return self.metadata[1]

    @property
    def samples(self) -> int:
        """
        ** The number of samples per channels. **

        Examples
        --------
        >>> from movia.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, 2, 1024).samples
        1024
        >>>
        """
        return self.shape[1]

    @property
    def time(self) -> Fraction:
        """
        ** The time of the first sample of the frame in second. **

        Examples
        --------
        >>> from movia.core.classes.frame_audio import FrameAudio
        >>> FrameAudio(0, 48000, 2, 1024).time
        Fraction(0, 1)
        >>>
        """
        return self.metadata[0]
