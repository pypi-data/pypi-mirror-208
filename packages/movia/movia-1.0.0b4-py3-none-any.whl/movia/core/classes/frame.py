#!/usr/bin/env python3

"""
** Defines the structure of a base frame, inerit from torch array. **
---------------------------------------------------------------------
"""

import abc

import torch



class Frame(torch.Tensor):
    """
    ** A General Frame. **

    Attributes
    ----------
    matadata : object
        Any information to throw during the transformations.
    """

    def __new__(cls, *args, metadata: object=None, **kwargs):
        """
        Parameters
        ----------
        metadata : object
            Any value to throw between the tensor operations.
        *args : tuple
            Transmitted to the `torch.Tensor` initialisator.
        **kwargs : dict
            Transmitted to the `torch.Tensor` initialisator.
        """
        frame = super().__new__(cls, *args, **kwargs)
        frame.metadata = metadata
        return frame

    def __repr__(self):
        """
        ** Allows to add metadata to the display. **

        Examples
        --------
        >>> from movia.core.classes.frame import Frame
        >>> Frame([0.0, 1.0, 2.0], metadata="matadata_value")
        Frame([0., 1., 2.], metadata='matadata_value')
        >>>
        """
        base = super().__repr__()
        return f"{base[:-1]}, metadata={repr(self.metadata)})"

    @classmethod
    def __torch_function__(cls, func, types, args=(), kwargs=None):
        """
        ** Enable to throw `metadata` into the new generations. **

        Examples
        --------
        >>> import torch
        >>> from movia.core.classes.frame import Frame
        >>> class Frame_(Frame):
        ...     def check_state(self):
        ...         assert self.item() # just for the example
        ...
        >>>
        >>> # transmission metadata
        >>> (frame := Frame_([.5], metadata="matadata_value"))
        Frame_([0.5000], metadata='matadata_value')
        >>> frame.clone() # deep copy
        Frame_([0.5000], metadata='matadata_value')
        >>> torch.sin(frame) # external call
        Frame_([0.4794], metadata='matadata_value')
        >>> frame / 2 # internal method
        Frame_([0.2500], metadata='matadata_value')
        >>> frame.numpy() # cast in an other type
        array([0.5], dtype=float32)
        >>> frame *= 2 # inplace
        >>> frame
        Frame_([1.], metadata='matadata_value')
        >>>
        >>> # cast if state not correct
        >>> torch.concatenate([frame, frame], axis=0) #
        tensor([1., 1.])
        >>> frame * 0 # no correct because has to be != 0
        tensor([0.])
        >>> frame *= 0
        >>> frame
        tensor([0.])
        >>>
        """
        if kwargs is None:
            kwargs = {}
        result = super().__torch_function__(func, types, args, kwargs)
        if isinstance(result, cls):
            if isinstance(args[0], cls): # args[0] is self
                result.metadata = args[0].metadata # args[0] is self
                try:
                    result.check_state()
                except AssertionError:
                    return torch.Tensor(result)
            else:
                return torch.Tensor(result)
        return result

    @abc.abstractmethod
    def check_state(self) -> None:
        """
        ** Apply verifications. **

        Raises
        ------
        AssertionError
            If something wrong in this frame.
        """
        raise NotImplementedError

    @property
    def shape(self) -> tuple[int]:
        """
        ** Solve pylint error E1136: Value 'self.shape' is unsubscriptable. **
        """
        return tuple(super().shape)
