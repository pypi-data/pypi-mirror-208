#!/usr/bin/env python3

"""
** Entry point of the graphic interface. **
-------------------------------------------
"""

import sys

import click

from movia.utils import get_project_root
from movia import __version__



@click.command()
@click.option("--test", is_flag=True, help="like movia-test")
@click.option("--gui", is_flag=True, help="like movia-gui")
def main(test: bool=False, gui: bool=False):
    """
    ** Global Layus of movia use. **
    """
    if test:
        from movia.testing.runtests import test as test_
        sys.exit(test_())
    if gui:
        from movia.gui.__main__ import main as main_
        sys.exit(main_())

    readme = get_project_root().parent / "README.rst"
    title = f"* MOVIA {__version__} *"
    print(
        f"{'*'*len(title)}\n{title}\n{'*'*len(title)}\n\n"
        f"For a detailed description, please refer to {readme} "
        "or https://framagit.org/robinechuca/movia.\n"
        "Run `movia-test` to check if the installation is correct.\n"
        "Run `movia-qt` to start the graphical user interface.\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
