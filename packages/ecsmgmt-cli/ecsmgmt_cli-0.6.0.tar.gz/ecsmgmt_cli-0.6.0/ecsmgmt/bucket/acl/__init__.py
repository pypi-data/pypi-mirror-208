import click

from ..._util.core import DynamicMultiCommandFactory

DynamicMultiCommand = DynamicMultiCommandFactory().create(__file__, __package__)


@click.command(cls=DynamicMultiCommand, name='acl')
def cli():
    """Manage bucket acl
    """
