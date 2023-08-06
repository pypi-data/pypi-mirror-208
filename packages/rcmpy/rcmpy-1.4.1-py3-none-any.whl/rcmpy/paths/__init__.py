"""
Common path lookups used by the package.
"""

# built-in
from contextlib import contextmanager
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Union

# third-party
from vcorelib.dict import limited

# internal
from rcmpy import PKG_NAME
from rcmpy.xdg import user_cache, user_config, user_state


def default_state_directory() -> Path:
    """Returns the default user-state directory used by the package."""
    return user_state(PKG_NAME)


def default_config_directory() -> Path:
    """Returns the default config directory used by the package."""
    return user_config(PKG_NAME, "default")


def default_cache_directory() -> Path:
    """Returns the default cache directory used by the package."""
    return user_cache(PKG_NAME)


@contextmanager
def override_environ(key: str, value: Union[Path, str]) -> Iterator[None]:
    """Override an environment variable as a managed context."""

    with limited(environ, key, str(value)):  # type: ignore
        yield


@contextmanager
def override_environ_tempdir(key: str) -> Iterator[Path]:
    """
    Set an environment variable to a temporary directory while it exists in
    the managed context.
    """

    with TemporaryDirectory() as tmpdir:
        with override_environ(key, tmpdir):
            yield Path(tmpdir)
