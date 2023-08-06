import os.path
import pathlib

import click
from ecsclient.client import Client

from ._util.callbacks import config_callback, namespace_callback
from ._util.const import CONTEXT_SETTINGS
from ._util.core import DynamicMultiCommandFactory

DynamicMultiCommand = DynamicMultiCommandFactory().create(__file__, __package__)


@click.command(cls=DynamicMultiCommand, context_settings=CONTEXT_SETTINGS)
@click.option(
    '-c', '--config', 'config_path',
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    default=os.path.join(click.get_app_dir('ecsmgmt-cli'), 'config.yml'),
    help='Configuration file in YAML format',
    callback=config_callback,
    is_eager=True,
    expose_value=False,
    show_default=True,
)
@click.option(
    '-n', '--namespace',
    type=click.STRING,
    callback=namespace_callback,
    expose_value=False,
    show_default=True,
)
@click.option(
    '-u', '--username',
    type=click.STRING,
    prompt=True,
    show_default=True,
)
@click.option(
    '-p', '--password',
    type=click.STRING,
    prompt=True,
    hide_input=True,
)
@click.option(
    '-e', '--endpoint', 'ecs_endpoint',
    type=click.STRING,
    help='ECS Management API Endpoint URI',
    show_default=True,
)
@click.pass_obj
def cli(obj: dict, username: str, password: str, ecs_endpoint: str):
    """Small CLI Client for the ECS Management API.
    """
    client = Client(
        version='3',
        username=username,
        password=password,
        ecs_endpoint=ecs_endpoint,
        token_endpoint=f'{ecs_endpoint}/login',
        cache_token=False,
    )
    obj['client'] = client
