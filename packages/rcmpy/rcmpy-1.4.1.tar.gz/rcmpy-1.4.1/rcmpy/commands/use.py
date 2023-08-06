"""
An entry-point for the 'use' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from rcmpy.commands.common import add_default_flag
from rcmpy.paths import default_config_directory
from rcmpy.state import load_state


def use_cmd(args: _Namespace) -> int:
    """Execute the use command."""

    with load_state() as state:
        if args.default:
            args.directory = default_config_directory()

        if args.directory is not None:
            state.set_directory(args.directory)

    return 0


def add_use_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add use-command arguments to its parser."""

    add_default_flag(parser)

    parser.add_argument(
        "directory", type=Path, nargs="?", help="the directory to use"
    )

    return use_cmd
