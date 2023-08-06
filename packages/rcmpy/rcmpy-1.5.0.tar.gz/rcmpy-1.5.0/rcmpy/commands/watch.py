"""
An entry-point for the 'watch' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from rcmpy.watch import watch
from rcmpy.watch.params import WatchParams


def watch_cmd(args: _Namespace) -> int:
    """Execute the watch command."""

    return watch(WatchParams.from_args(args))


def add_watch_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add watch-command arguments to its parser."""

    WatchParams.add_args(parser)
    return watch_cmd
