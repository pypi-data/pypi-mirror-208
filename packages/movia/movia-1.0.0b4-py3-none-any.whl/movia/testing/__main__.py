#!/usr/bin/env python3

"""
** Alias for ``movia.testing.runtests`` **
------------------------------------------
"""

import sys

from movia.testing.runtests import test

if __name__ == "__main__":
    sys.exit(test())
