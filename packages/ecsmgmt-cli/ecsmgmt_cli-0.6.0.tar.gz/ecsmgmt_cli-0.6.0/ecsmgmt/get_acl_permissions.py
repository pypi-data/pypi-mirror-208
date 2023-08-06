import click

from ._util.format import pretty_info


@click.command()
@click.pass_obj
def cli(obj: dict):
    """Get acl permissions
    """
    client = obj['client']

    res = client.bucket.get_acl_permissions()

    click.secho('Available acl permissions:', bold=True)
    click.echo(pretty_info(res))
