"""
A module implementing this package's stateful information that persists across
invocations.
"""

# built-in
from contextlib import ExitStack, contextmanager
from io import StringIO
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Iterator, List, cast

# third-party
from jinja2 import Template
from vcorelib.dict import merge
from vcorelib.dict.cache import FileCache
from vcorelib.io import ARBITER
from vcorelib.io.types import DataStream
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike, normalize, rel

# internal
from rcmpy.paths import default_config_directory, default_state_directory
from rcmpy.schemas import RcmpyDictCodec as _RcmpyDictCodec

LOG = getLogger(__name__)


class State(_RcmpyDictCodec):
    """The top-level configuration object for the package."""

    directory: Path
    variant: str
    variables_new: bool
    configs_new: bool
    manifest: Dict[str, Any]
    manifest_new: bool

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        self.logger = LOG

        self.directory = normalize(
            cast(str, data.get("directory", default_config_directory()))
        ).resolve()

        self.logger.info("Using directory '%s'.", rel(self.directory))

        self.variant: str = cast(str, data["variant"])
        if self.variant:
            self.logger.info("Using variant '%s'.", self.variant)

        data.setdefault("previous", {})
        self.previous: Dict[str, Any] = data["previous"]  # type: ignore
        self.previous.setdefault("variant", "default")

        # Variables.
        self.variables: Dict[str, Any] = {}
        self.variables_new = False
        self.previous.setdefault("variables", {})
        self._load_variables()

        # Configs.
        self.configs: Dict[str, Any] = {}
        self.configs_new = False
        self.previous.setdefault("configs", {})
        self._load_configs()

        # Manifest configuration.
        self.manifest: Dict[str, Any] = cast(
            Dict[str, Any], data.get("manifest", {})
        )
        self.manifest_new: bool = False

    def is_new(self) -> bool:
        """Determine if state has changed."""
        return (
            self.variant != self.previous["variant"]
            or self.variables_new
            or self.configs_new
            or self.manifest_new
        )

    def update_manifest(self, data: Dict[str, Any]) -> None:
        """Set new manifest data."""
        self.manifest_new = self.manifest != data
        self.manifest = data

    def root_directories(
        self, subdir: str, common_first: bool = True
    ) -> List[Path]:
        """
        Get up to a pair of directories from some sub-directory of the current
        root.
        """

        root = self.directory.joinpath(subdir)

        candidates = [root.joinpath("common")]
        if self.variant:
            if common_first:
                candidates.append(root.joinpath(self.variant))
            else:
                candidates.insert(0, root.joinpath(self.variant))

        return [x for x in candidates if x.is_dir()]

    def _load_configs(self) -> None:
        """Load data for configs."""

        with ExitStack() as stack:

            def preprocessor(stream: DataStream) -> DataStream:
                """Render the variable file as a template."""

                return stack.enter_context(
                    StringIO(Template(stream.read()).render(self.variables))
                )

            for path in self.root_directories("configs"):
                merge(
                    self.configs,
                    ARBITER.decode_directory(
                        path,
                        logger=self.logger,
                        require_success=True,
                        recurse=True,
                        includes_key="includes",
                        expect_overwrite=True,
                        preprocessor=preprocessor,
                    ).data,
                    expect_overwrite=True,
                    logger=self.logger,
                )

        self.configs_new = self.configs != self.previous["configs"]
        self.previous["configs"] = self.configs

        if self.configs_new:
            self.logger.info("Configuration data is updated.")

    def _load_variables(self) -> None:
        """Load data for variables."""

        for path in self.root_directories("variables"):
            merge(
                self.variables,
                ARBITER.decode_directory(
                    path,
                    logger=self.logger,
                    require_success=True,
                    recurse=True,
                    includes_key="includes",
                    expect_overwrite=True,
                ).data,
                expect_overwrite=True,
                logger=self.logger,
            )

        self.variables_new = self.variables != self.previous["variables"]
        self.previous["variables"] = self.variables

        if self.variables_new:
            self.logger.info("Variable data is updated.")

    def set_directory(self, path: Pathlike) -> None:
        """Set a new directory to use as the data repository."""

        new_dir = normalize(path).resolve()

        if new_dir == self.directory:
            self.logger.info(
                "New directory '%s' same as current.", rel(new_dir)
            )
            return

        self.directory = new_dir
        self.logger.info("Set directory to '%s'.", rel(new_dir))

    def set_variant(self, variant: str = None) -> None:
        """Set a new variant value."""

        if not variant:
            self.logger.info("Current variant: '%s'.", self.variant)
        elif variant != self.variant:
            self.previous["variant"] = self.variant
            self.variant = variant
            self.logger.info("Updating variant to '%s'.", variant)

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        return {
            "directory": str(self.directory),
            "variant": self.variant,
            "previous": self.previous,
            "manifest": self.manifest,
        }


@contextmanager
def load_state(
    root: Pathlike = None, name: str = "state.json"
) -> Iterator[State]:
    """This needs to be a context manager, so it get's written back to disk."""

    if root is None:
        root = default_state_directory()

    with FileCache(normalize(root, name)).loaded() as data:
        state = State.create(data, verify=False)
        yield state

        # Update the original dictionary with any changes to the state object.
        data.update(state.asdict())
