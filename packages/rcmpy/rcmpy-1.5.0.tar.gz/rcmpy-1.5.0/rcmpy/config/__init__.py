"""
A module implementing a configuration interface for the package.
"""

# built-in
from os.path import expandvars
from pathlib import Path
from typing import Any, Dict, List, Set, cast

# third-party
from vcorelib.dict.codec import BasicDictCodec as _BasicDictCodec
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from rcmpy.config.file import ManagedFile
from rcmpy.schemas import RcmpyDictCodec as _RcmpyDictCodec

FilesConfig = List[Dict[str, Any]]

__all__ = ["FilesConfig", "Config", "ManagedFile"]


class Config(_RcmpyDictCodec, _BasicDictCodec):
    """The top-level configuration object for the package."""

    def update_root(self, root: Path) -> None:
        """Call 'update_root' for each managed file."""

        for file in self.files:
            file.update_root(root)

    def init(self, data: _JsonObject) -> None:
        """Initialize this instance."""
        self.data = data

        # A set of templates that are used by this config.
        self.templates: Set[str] = set()

        self.files: List[ManagedFile] = []
        for file in cast(FilesConfig, data.get("files", [])):
            new = ManagedFile(
                file["template"],
                set(file.get("extra_templates", [])),
                # Resolve environment variables and any '~' here.
                Path(expandvars(file["directory"])).expanduser(),
                file.get("name", file["template"]),
                file["link"],
                file["executable"],
                file["condition"],
                set(file.get("platforms", [])),
            )

            # Keep track of all templates used in any file.
            self.templates.add(new.template)
            for template in new.extra_templates:
                self.templates.add(template)

            self.files.append(new)
