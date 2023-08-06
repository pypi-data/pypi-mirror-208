"""
An interface for implementing file-system watching parameters.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path
from typing import List, NamedTuple

DEFAULT_POLL_RATE = 0.1


class WatchParams(NamedTuple):
    """Watch task parameters."""

    base: Path
    directory: Path
    cmd: List[str]
    check_contents: bool
    shell: bool = False
    single_pass: bool = False
    poll_rate: float = DEFAULT_POLL_RATE

    @staticmethod
    def from_args(args: _Namespace) -> "WatchParams":
        """Create watch parameters from parsed arugments."""

        return WatchParams(
            args.dir,
            args.directory,
            args.cmd,
            not args.no_change,
            args.shell,
            args.single_pass,
            args.poll_rate,
        )

    @staticmethod
    def add_args(parser: _ArgumentParser) -> None:
        """Add command-line argument options."""

        parser.add_argument(
            "-p",
            "--poll-rate",
            type=float,
            default=DEFAULT_POLL_RATE,
            help="poll period in seconds (default: %(default)ss)",
        )
        parser.add_argument(
            "-s",
            "--shell",
            action="store_true",
            help="set to run a shell command",
        )
        parser.add_argument(
            "-i",
            "--single-pass",
            action="store_true",
            help="only run a single iteration",
        )
        parser.add_argument(
            "-n",
            "--no-change",
            action="store_true",
            help=(
                "don't act on changed files, only the overall "
                "set of files changing (added or removed)"
            ),
        )
        parser.add_argument(
            "directory", type=Path, help="directory to watch for file changes"
        )
        parser.add_argument("cmd", nargs="+", help="command to run")
