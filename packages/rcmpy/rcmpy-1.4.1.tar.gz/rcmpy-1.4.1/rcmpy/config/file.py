"""
A module implementing an interface for package-managed files.
"""

# built-in
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from shutil import copyfile
import sys
from typing import Any, Dict, Set

# third-party
from vcorelib.logging import LoggerType
from vcorelib.paths import rel


def set_exec_flags(path: Path) -> None:
    """Set the executable bits, but respect the 'read' bits."""
    mode = path.stat().st_mode
    path.chmod(mode | ((mode & 0o444) >> 2))


@dataclass
class ManagedFile:
    """
    A data structure for managed files specified in the configuration data.
    """

    template: str
    extra_templates: Set[str]

    directory: Path
    name: str

    link: bool
    executable: bool

    condition: str

    platforms: Set[str]

    @property
    def output(self) -> Path:
        """Get the full output path."""
        return self.directory.joinpath(self.name)

    @property
    def present(self) -> bool:
        """Determine if this file is currently present in the file system."""
        return self.output.is_file()

    @property
    def platform(self) -> bool:
        """Determine if the platform is correct for handling this file."""
        return not self.platforms or sys.platform in self.platforms

    def evaluate(self, env: Dict[str, Any]) -> bool:
        """Determine if this file should be handled."""
        return self.platform and eval(  # pylint: disable=eval-used
            self.condition, None, env
        )

    def update_root(self, root: Path) -> None:
        """
        If the output directory is a relative path, update it to be an
        absolute one based on the provided root directory.
        """

        if not self.directory.is_absolute():
            self.directory = root.joinpath(self.directory)
            assert self.directory.is_absolute(), self.directory

    def update(self, source: Path, logger: LoggerType) -> None:
        """Update this managed file based on the provided source file."""

        output = self.output

        # At some point this could be skipped for existing symlinks.
        with suppress(FileNotFoundError):
            output.unlink()

        # Ensure the output directory exists.
        self.directory.mkdir(parents=True, exist_ok=True)

        if self.link:
            output.symlink_to(source)
        else:
            copyfile(source, output)

        if self.executable:
            set_exec_flags(output)

        logger.info("'%s' -> '%s'.", rel(source), rel(output))
