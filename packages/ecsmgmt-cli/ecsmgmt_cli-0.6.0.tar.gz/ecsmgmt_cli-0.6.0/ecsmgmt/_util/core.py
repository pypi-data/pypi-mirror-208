"""Implements enhancments for click core utilities"""

import importlib
import pathlib
from typing import Optional

import click


class DynamicMultiCommandFactory:
    """A factory to make configurable dynamic click.MultiCommand

    The main purpose of the factory is the configuration of the dynamic click.MultiCommand.
    It is a quirk, but currently there is no better implentation for this purpose.
    Feel free to find a better solution.
    """

    def create(self, parent_path: str, base_package: str) -> type[click.MultiCommand]:
        """Create a DynamicMultiCommand and uses parent_path as search path.

        Keyword arguments:
        parent_path -- search parent_path for sub commands
        base_package -- base package from where the subcommands are imported
        """

        # strip parent filename from path
        plugin_path = pathlib.Path(parent_path).parent

        class DynamicMultiCommand(click.MultiCommand):
            """A dynamic Multicommand implementation of click.MultiCommand

            Commands are dynamically """

            def list_commands(self, ctx: click.Context) -> list[str]:
                commands = []
                for path in plugin_path.iterdir():
                    if path.name.startswith('_'):
                        continue

                    if path.suffix == '.py':
                        commands.append(path.stem.replace('_', '-'))
                    elif path.is_dir():
                        commands.append(path.name.replace('_', '-'))

                commands.sort()
                return commands

            def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
                commands = self.list_commands(ctx)
                command_candidates = [c for c in commands if c.startswith(cmd_name)]

                command = None
                if len(command_candidates) == 1:
                    command = command_candidates[0]
                elif len(command_candidates) > 1:
                    ctx.fail('Too many command matches: {matches}'.format(
                        matches=', '.join(sorted(command_candidates))))

                if command is None:
                    return_command = None
                else:
                    try:
                        command_module = importlib.import_module('.{name}'.format(name=command.replace('-', '_')),
                                                                 base_package)
                        return_command = command_module.cli
                    except ModuleNotFoundError:
                        return_command = None

                return return_command

        return DynamicMultiCommand
