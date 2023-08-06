"""
An entry-point for the 'variant' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from rcmpy.commands.common import add_default_flag
from rcmpy.state import load_state


def variant_cmd(args: _Namespace) -> int:
    """Execute the variant command."""

    with load_state() as state:
        if args.default:
            args.variant = "default"

        state.set_variant(args.variant)

    return 0


def add_variant_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add variant-command arguments to its parser."""

    add_default_flag(parser)

    parser.add_argument("variant", nargs="?", help="new variant to use")
    return variant_cmd
