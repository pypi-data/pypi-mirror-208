"""
An entry-point for the 'dump' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from json import dump
import sys

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from rcmpy.commands.common import run_env_command
from rcmpy.environment import Environment


def dump_env(_: _Namespace, env: Environment) -> int:
    """Dump information about the environment."""

    dump(env.template_data, sys.stdout, indent=2, sort_keys=True)
    return 0


def dump_cmd(args: _Namespace) -> int:
    """Execute the dump command."""
    return run_env_command(args, dump_env)


def add_dump_cmd(_: _ArgumentParser) -> _CommandFunction:
    """Add dump-command arguments to its parser."""

    return dump_cmd
