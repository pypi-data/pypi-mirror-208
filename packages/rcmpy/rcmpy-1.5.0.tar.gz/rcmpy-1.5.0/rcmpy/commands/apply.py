"""
An entry-point for the 'apply' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.paths import rel

# internal
from rcmpy.commands.common import run_env_command
from rcmpy.environment import Environment


def apply_env(args: _Namespace, env: Environment) -> int:
    """Apply pending changes from the environment."""

    result = 0

    is_new = env.state.is_new()

    for file in env.config.files:
        # Check if a template is found for this file.
        if file.template not in env.templates_by_name:
            result += 1
            env.logger.error("Template '%s' not found!", file.template)
            continue

        if not file.evaluate(env.env_data):
            continue

        # Check if this file has any updated templates.
        if args.force or is_new or not file.present or env.is_updated(file):
            template = env.templates_by_name[file.template]

            # If a template doesn't require rendering, use it as-is.
            source = template.path

            if template.template is not None:
                # Render the template to the build directory.
                source = env.build.joinpath(file.template)
                with source.open("w") as path_fd:
                    path_fd.write(template.template.render(env.template_data))
                    env.logger.info("Rendered '%s'.", rel(source))

            # Update the output file.
            if not args.dry_run:
                file.update(source, env.logger)

    return result


def apply_cmd(args: _Namespace) -> int:
    """Execute the apply command."""
    return run_env_command(args, apply_env)


def add_apply_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add apply-command arguments to its parser."""

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether or not to forcibly render all outputs",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="whether or not to update output files",
    )

    return apply_cmd
