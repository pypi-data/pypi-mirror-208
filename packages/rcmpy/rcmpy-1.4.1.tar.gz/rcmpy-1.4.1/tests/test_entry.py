"""
rcmpy - Test the program's entry-point.
"""

# built-in
from subprocess import check_output
from sys import executable
from unittest.mock import patch

# module under test
from rcmpy import PKG_NAME
from rcmpy.entry import main as rcmpy_main


def test_entry_basic():
    """Test basic argument parsing."""

    args = [PKG_NAME]
    assert rcmpy_main(args + ["-h"]) == 0

    with patch("rcmpy.entry.entry", side_effect=SystemExit(1)):
        assert rcmpy_main(args) != 0


def test_package_entry():
    """Test the command-line entry through the 'python -m' invocation."""

    check_output([executable, "-m", "rcmpy", "-h"])
