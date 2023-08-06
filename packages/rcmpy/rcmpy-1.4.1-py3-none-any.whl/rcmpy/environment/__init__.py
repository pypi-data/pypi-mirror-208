"""
A module implementing the package's runtime environment.
"""

# built-in
from contextlib import ExitStack, contextmanager
from typing import Iterator

# third-party
from vcorelib.paths import Pathlike

# internal
from rcmpy.environment.template import TemplateEnvironment
from rcmpy.state import load_state


class Environment(TemplateEnvironment):
    """A class implementing this package's runtime environment."""


@contextmanager
def load_environment(
    root: Pathlike = None, name: str = "state.json"
) -> Iterator[Environment]:
    """A wrapper for loading an environment with default state data."""

    with ExitStack() as stack:
        env = Environment(
            stack.enter_context(load_state(root=root, name=name)), stack
        )
        yield env

        # Ensure that the previous variant gets set.
        env.state.previous["variant"] = env.state.variant
