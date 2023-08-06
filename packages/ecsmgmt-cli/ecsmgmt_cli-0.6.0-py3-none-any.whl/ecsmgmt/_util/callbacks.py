import pathlib

import click
import yaml


def config_callback(ctx: click.Context, param: click.ParamType, config_path: pathlib.Path):
    configpath = config_path.expanduser().resolve()

    try:
        with configpath.open('r') as infile:
            config = yaml.safe_load(infile.read())
    except FileNotFoundError:
        return

    defaults = dict(config.pop('defaults', {}))

    if not isinstance(ctx.command, click.MultiCommand):
        raise click.ClickException('Something has gone horribly wrong. This is a developer error, please contact them.')

    ctx.default_map = ctx.default_map or {}  # preserve existing defaults
    ctx.default_map.update(defaults)

    ctx.ensure_object(dict)
    ctx.obj['config'] = config


def namespace_callback(ctx: click.Context, param: click.ParamType, namespace: str):
    ctx.ensure_object(dict)
    config = ctx.obj['config']
    ctx.obj['namespace'] = namespace

    namespace_config = config.get('namespaces', {}).get(namespace, {})

    ctx.default_map = ctx.default_map or {}  # preserve existing defaults
    ctx.default_map.update(namespace_config)
