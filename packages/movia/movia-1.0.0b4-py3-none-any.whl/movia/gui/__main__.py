#!/usr/bin/env python3

"""
** Entry point of the GUI. **
------------------------------
"""

import pathlib
import signal
import sys
import traceback

import click

from PyQt6 import QtWidgets
from movia.gui.main import MainWindow



@click.command()
@click.argument(
    "project_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
)
def main(project_file: pathlib.Path=None) -> int:
    """
    ** Start the GUI. **
    """
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    # soft ctrl+c management, replace lambda by signal.SIG_DFL for fast closing
    signal.signal(signal.SIGINT, lambda *_: app.quit())

    # create the window
    window = MainWindow()
    if project_file is not None:
        window.open(project_file)
    window.showMaximized()
    window.refresh()

    # catch and show global exceptions
    def crach_except_hook(exc, value, tb_):
        msg = "".join(traceback.format_exception(exc, value, tb_))
        sys.stderr.write(msg)
        window.crash(msg)
        app.quit()
    sys.excepthook = crach_except_hook

    code = app.exec()
    return code


if __name__ == '__main__':
    main()
