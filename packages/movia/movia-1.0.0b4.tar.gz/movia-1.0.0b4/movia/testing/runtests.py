#!/usr/bin/env python3

"""
** Executes all the tests via the ``pytest`` module. **
-------------------------------------------------------
"""

import sys

import click

try:
    from pylint.lint import Run as PylintRun
except ImportError as err:
    raise ImportError("pylint paquage required (pip install movia[optional])") from err
try:
    import pytest
except ImportError as err:
    raise ImportError("pytest paquage required (pip install movia[optional])") from err

from movia.utils import get_project_root


@click.command()
@click.option("--light", is_flag=True, help="performs only some light tests")
def test(light=False) -> int:
    """
    ** Performs all unit tests. **
    """
    # ffprobe -v error -show_program_version -of json
    # ffmpeg -version
    # ffprobe -version

    root = get_project_root()
    paths = (
        [str(root / "utils.py")]
        + [str(root / "core")]
        + sorted(str(p) for p in (root / "testing" / "tests").rglob("*.py"))
    )
    if (code := pytest.main(["-m", "not slow", "--full-trace", "--doctest-modules"] + paths)):
        return int(code)
    if not light:
        if (code := (
            PylintRun(["--rcfile", str(root.parent / ".pylintrc"), str(root)], exit=False)
            .linter.msg_status
        )):
            return code
    if not light:
        if (code := pytest.main(["-m", "slow", "--full-trace", "--verbose"] + paths)):
            return int(code)
    return 0

if __name__ == "__main__":
    sys.exit(test())
