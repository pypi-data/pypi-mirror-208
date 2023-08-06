"""
A module for common argument-parsing methods.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from logging import getLogger
from typing import Callable

# third-party
from vcorelib.logging import log_time

# internal
from rcmpy.environment import Environment, load_environment


def add_default_flag(parser: _ArgumentParser) -> None:
    """Adds a default-flag argument."""

    parser.add_argument(
        "-d",
        "--default",
        action="store_true",
        help="sets the directory back to the package default",
    )


EnvCommand = Callable[[_Namespace, Environment], int]


def run_env_command(args: _Namespace, cmd: EnvCommand) -> int:
    """Run a command with the environment instance loaded."""

    result = 1

    with log_time(getLogger(__name__), "Command"):
        with load_environment() as env:
            if env.config_loaded:
                result = cmd(args, env)

    return result
