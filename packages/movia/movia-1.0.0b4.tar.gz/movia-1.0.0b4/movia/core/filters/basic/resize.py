#!/usr/bin/env python3

"""
** Resizes an image while keeping the proportions. **
-----------------------------------------------------
"""

import numbers
import typing

import cv2
import numpy as np

from movia.core.classes.frame_video import FrameVideo



def resize_keep_ratio(
    frame: typing.Union[np.ndarray, FrameVideo],
    shape: typing.Union[tuple[numbers.Integral, numbers.Integral], list[numbers.Integral]],
) -> typing.Union[np.ndarray, FrameVideo]:
    """
    ** Resizes an image while keeping the proportions. **

    Parameters
    ----------
    frame : np.ndarray or movia.core.classes.frame_video.FrameVideo
        The image to be resized. If a numpy array is provide, the format
        has to match with the video frame specifications.
    shape : int and int
        The pixel dimensions of the returned frame.
        The convention adopted is the numpy convention (height, width).

    Returns
    -------
    np.ndarray or movia.core.classes.frame_video.FrameVideo
        The resized frame homogeneous with the input.
        The underground datas are not sharded with the input. A safe copy is done.
        In order to keep the proportion of the image, transparent bands can be appended.

    Examples
    --------
    >>> import torch
    >>> from movia.core.classes.frame_video import FrameVideo
    >>> from movia.core.filters.basic.resize import resize_keep_ratio
    >>> ref = FrameVideo(0, torch.full((50, 100, 4), 128, dtype=torch.uint8))
    >>> resize_keep_ratio(ref, (8, 8))[..., 3] # alpha
    tensor([[  0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0]], dtype=torch.uint8)
    >>> resize_keep_ratio(ref, (8, 8)).convert(1)[..., 0] # as gray
    tensor([[  0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128, 128, 128, 128],
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [  0,   0,   0,   0,   0,   0,   0,   0]], dtype=torch.uint8)
    >>>
    """
    # case FrameVideo
    if isinstance(frame, FrameVideo):
        return FrameVideo(frame.time, resize_keep_ratio(frame.numpy(force=True), shape))

    # verif case np.ndarray
    assert isinstance(frame, np.ndarray), frame.__class__.__name__
    assert frame.ndim == 3, frame.shape
    assert frame.shape[0] >= 1, frame.shape
    assert frame.shape[1] >= 1, frame.shape
    assert frame.shape[2] in {1, 2, 3, 4}, frame.shape
    assert frame.dtype == np.uint8, frame.dtype
    assert len(shape) == 2, len(shape)
    assert all(isinstance(s, numbers.Integral) and s >= 1 for s in shape), shape

    # operation case np.ndarray
    shape_in = (int(frame.shape[0]), int(frame.shape[1]))
    shape_dst = (int(shape[0]), int(shape[1]))
    if shape_in == shape_dst:
        return np.copy(frame)
    shape_prop = (shape_dst[0], shape_in[1]*shape_dst[0]/shape_in[0]) # try h unchanged
    if shape_prop[1] > shape_dst[1]: # if to big
        shape_prop = (shape_in[0]*shape_dst[1]/shape_in[1], shape_dst[1]) # keep w unchanged
    if abs(shape_prop[0] - shape_dst[0]) < 1: # if the dimension almost corresponds (h)
        shape_prop = (shape_dst[0], shape_prop[1]) # we make it match perfectly
    if abs(shape_prop[1] - shape_dst[1]) < 1: # if the dimension almost corresponds (w)
        shape_prop = (shape_prop[0], shape_dst[1]) # we make it match perfectly
    shape_prop = (max(1, round(shape_prop[0])), max(1, round(shape_prop[1]))) # cast to int
    frame_prop = cv2.resize(frame, shape_prop[::-1], interpolation=cv2.INTER_LINEAR)
    if shape_dst == shape_prop: # if we dont need to pad
        return frame_prop

    # pad
    channels = {1: 2, 2: 2, 3: 4, 4: 4}[frame_prop.shape[2]]
    frame_paded = np.empty((*shape_dst, channels), dtype=np.uint8) # 1500 faster np.zeros
    if shape_dst[0] == shape_prop[0]: # if h match
        dec = (shape_dst[1]-shape_prop[1])//2
        frame_paded[:, dec:shape_prop[1]+dec, :frame_prop.shape[2]] = frame_prop
        if frame_prop.shape[2] != channels: # if no alpha specify
            frame_paded[:, dec:shape_prop[1]+dec, -1] = 255 # blind
        frame_paded[:, :dec, -1] = 0 # set band transparent
        frame_paded[:, shape_prop[1]+dec:, -1] = 0
    else: # if w match
        dec = (shape_dst[0]-shape_prop[0])//2
        frame_paded[dec:shape_prop[0]+dec, :, :frame_prop.shape[2]] = frame_prop
        if frame_prop.shape[2] != channels: # if no alpha specify
            frame_paded[dec:shape_prop[0]+dec, :, -1] = 255 # blind
        frame_paded[:dec, :, -1] = 0 # set band transparent
        frame_paded[shape_prop[0]+dec:, :, -1] = 0
    return frame_paded
