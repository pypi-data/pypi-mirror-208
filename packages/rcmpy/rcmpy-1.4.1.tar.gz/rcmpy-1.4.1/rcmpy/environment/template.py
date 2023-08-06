"""
An environment extension for working with template files.
"""

# built-in
from copy import copy
from pathlib import Path
from typing import Dict, NamedTuple, Optional, Set, Tuple

# third-party
from datazen.templates import environment
from jinja2 import Environment, FileSystemLoader, Template
from vcorelib.paths.info import FileChangeEvent
from vcorelib.paths.info_cache import FileChanged, file_info_cache

# internal
from rcmpy.config import ManagedFile
from rcmpy.environment.base import BaseEnvironment
from rcmpy.environment.data import system_data


class EnvTemplate(NamedTuple):
    """
    A data structure for keeping track of environment templates. If 'template'
    is None, it signals that the template does not require rendering.
    """

    name: str
    path: Path
    subdir: str
    template: Optional[Template] = None


def template_name(name: str) -> Tuple[bool, str]:
    """
    Determine if a name is a template and remove the template suffix if
    applicable.
    """

    is_template = name.endswith(".j2")
    if is_template:
        name = name[:-3]
    return is_template, name


class TemplateEnvironment(BaseEnvironment):
    """
    A class implementing template management for this package's runtime
    environment.
    """

    templates: Dict[Path, EnvTemplate]
    templates_by_name: Dict[str, EnvTemplate]
    jinja: Environment

    def is_updated(self, file: ManagedFile) -> bool:
        """
        Determine if a managed file is updated or not (based on template
        changes).
        """
        return file.template in self.updated_template_names or any(
            x in self.updated_template_names for x in file.extra_templates
        )

    def _load_templates(self) -> None:
        """Load template information to the environment."""

        # Keep track of templates by name.
        self.templates = {}
        self.templates_by_name = {}
        for name in self.jinja.list_templates():
            obj = self.jinja.get_template(name)

            # We know all templates are files.
            assert obj.filename is not None

            is_template, name = template_name(name)

            # Keep track of template paths and their templates.
            path = Path(obj.filename).resolve()

            new = EnvTemplate(
                name,
                path,
                path.parent.name,
                obj if is_template else None,
            )
            self.templates[path] = new
            self.templates_by_name[name] = new

    def _init_templates(self, template_names: Set[str]) -> bool:
        """
        Initialize the template environment based on a set of template names
        that may be relevant to some task.
        """

        # The variant's template directory takes precedence.
        candidates = self.state.root_directories(
            "templates", common_first=False
        )

        # Prefer variant templates, if the variant template-directory
        # exists.
        self.jinja = environment(
            loader=FileSystemLoader(candidates, followlinks=True)
        )

        self._load_templates()

        def poll_cb(change: FileChanged) -> bool:
            """Aggregate paths of templates that have been updated."""

            if change.event is not FileChangeEvent.REMOVED:
                assert change.new is not None
                path = change.new.path

                subdir = path.parent.name
                _, name = template_name(path.name)

                # Don't acknowledge changes to any files that aren't active
                # templates.
                if (
                    name not in template_names
                    or name not in self.templates_by_name
                ):
                    return False

                template = self.templates_by_name[name]

                # If a version of a template that's not currently used has
                # changed, don't acknowledge the change either.
                if subdir != template.subdir:
                    return False

                self.updated_templates.add(path)
                self.updated_template_names.add(self.templates[path].name)

            return True

        template_changes = self.stack.enter_context(
            file_info_cache(
                self._cache.joinpath("templates.json"),
                poll_cb,
                logger=self.logger,
            )
        )

        # Poll template directories.
        for candidate in candidates:
            template_changes.poll_directory(candidate)

        # Log info about detected template changes.
        for changed in self.updated_templates:
            template = self.templates[changed]
            self.logger.info(
                "Detected change for template '%s' (%s).",
                template.name,
                template.subdir,
            )

        return True

    def _init_loaded(self) -> bool:
        """Called during initialization if a valid configuration is loaded."""

        result = super()._init_loaded()

        # Ensure double initialization isn't possible (use an arbitrary
        # attribute set here to detect this).
        assert not hasattr(self, "jinja")

        # Templates that are newly updated on this iteration.
        self.updated_templates: Set[Path] = set()
        self.updated_template_names: Set[str] = set()

        # Add additional information to template data.
        self.env_data = system_data()
        self.template_data = copy(self.state.configs)
        assert "env" not in self.template_data
        self.template_data["env"] = self.env_data

        return result and self._init_templates(self.config.templates)
