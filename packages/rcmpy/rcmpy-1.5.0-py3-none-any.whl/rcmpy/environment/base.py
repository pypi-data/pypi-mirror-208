"""
A module implementing a basic environment interface.
"""

# built-in
from contextlib import ExitStack
from pathlib import Path
from typing import Optional

# third-party
from vcorelib.io import ARBITER
from vcorelib.io.types import FileExtension, LoadResult
from vcorelib.logging import LoggerMixin, LoggerType
from vcorelib.paths import Pathlike, normalize, rel

# internal
from rcmpy import PKG_NAME
from rcmpy.config import Config
from rcmpy.paths import default_cache_directory
from rcmpy.state import State


def load_if_single_candidate(
    path: Pathlike, logger: LoggerType = None
) -> Optional[LoadResult]:
    """
    Attempt to load a configuration file if a candidate exists at the given
    path.
    """

    result = None
    path = normalize(path)

    config_candidates = list(
        FileExtension.data_candidates(path, exists_only=True)
    )

    if not config_candidates:
        if logger is not None:
            logger.error(
                "No config found: %s.",
                list(str(x) for x in FileExtension.data_candidates(path)),
            )
    elif len(config_candidates) == 1:
        result = ARBITER.decode(
            config_candidates[0],
            includes_key="includes",
            expect_overwrite=True,
        )
        if logger is not None:
            logger.info("Loaded config '%s'.", rel(config_candidates[0]))

    return result


def load_manifest(
    root: Path, variant: str, logger: LoggerType
) -> Optional[LoadResult]:
    """Load the top-level data repository configuration."""

    # Attempt to load the base manifest.
    config_data = load_if_single_candidate(
        root.joinpath(PKG_NAME), logger=logger
    )

    if config_data is not None:
        # Attempt to load variant-specific manifest data.
        variant_data = load_if_single_candidate(
            root.joinpath("includes", variant)
        )
        if variant_data is not None:
            config_data.merge(variant_data, expect_overwrite=True)

    return config_data


class BaseEnvironment(LoggerMixin):
    """A class implementing this package's base runtime environment."""

    def __init__(self, state: State, stack: ExitStack) -> None:
        """Initialize this instance."""

        super().__init__()
        self.state = state
        self.stack = stack
        self._config: Optional[Config] = None
        self._cache = default_cache_directory()

        self.build = state.directory.joinpath("build")
        self.build.mkdir(exist_ok=True)

        config_data = load_manifest(
            state.directory, state.variant, self.logger
        )
        if config_data is not None:
            self._config = Config(data=config_data.data)

            # Ensure that any relative paths called out are relative to the
            # root directory of the data repository.
            self._config.update_root(state.directory)

            # Treat manifest changes as criteria for updating outputs.
            self.state.update_manifest(self._config.data)

            # Consider the config not loaded if initialization fails.
            #
            # **Add this back in if initialization can actually fail.**
            #
            # if not self._init_loaded():
            #     self.logger.info("Initialization failed!")
            #     self._config = None
            assert self._init_loaded()

    def _init_loaded(self) -> bool:
        """Called during initialization if a valid configuration is loaded."""
        return True

    @property
    def config_loaded(self) -> bool:
        """Determine if this environment has loaded a config."""
        return self._config is not None

    @property
    def config(self) -> Config:
        """Get this environment's configuration object."""
        assert self._config is not None, "Config not loaded!"
        return self._config
