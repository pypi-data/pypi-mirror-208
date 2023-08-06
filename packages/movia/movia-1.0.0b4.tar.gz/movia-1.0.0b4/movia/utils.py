#!/usr/bin/env python3

"""
** Pythonic tools. **
---------------------
"""

import pathlib



def get_project_root() -> pathlib.Path:
    """
    ** Returns project root folder. **

    Examples
    --------
    >>> from movia.utils import get_project_root
    >>> root = get_project_root()
    >>> root.is_dir()
    True
    >>> root.name
    'movia'
    >>> sorted(p.name for p in root.iterdir())
    ['__init__.py', '__main__.py', '__pycache__', 'core', 'examples', 'gui', 'testing', 'utils.py']
    >>>
    """
    return pathlib.Path(__file__).parent
