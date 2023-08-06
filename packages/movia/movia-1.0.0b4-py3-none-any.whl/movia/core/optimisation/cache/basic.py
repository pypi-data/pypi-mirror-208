#!/usr/bin/env python3

"""
** The not sofisticated cache decorators. **
--------------------------------------------
"""

import functools


def basic_cache(func: callable) -> callable:
    """
    ** Cache for hashable args. **

    Examples
    --------
    >>> from movia.core.optimisation.cache.basic import basic_cache
    >>> i = 0
    >>> @basic_cache
    ... def f(x):
    ...     global i
    ...     i += x
    ...     return i
    ...
    >>> f(1)
    1
    >>> f(1)
    1
    >>>
    """
    @functools.wraps(func)
    def cached_func(*args, **kwargs):
        signature = (args, tuple((k, kwargs[k]) for k in sorted(kwargs)))
        func.cache = getattr(func, "cache", {})
        if signature not in func.cache:
            func.cache[signature] = func(*args, **kwargs)
        return func.cache[signature]

    return cached_func
