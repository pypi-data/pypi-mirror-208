import click

from .._util.format import pretty_info


@click.command()
@click.argument('user-id', type=click.STRING)
@click.pass_obj
def cli(obj: dict, user_id: str):
    """Get user details
    """
    client = obj['client']
    namespace = obj['namespace']

    res = client.object_user.get(user_id=user_id, namespace=namespace)

    click.secho(f'User "{user_id}" info:', bold=True)
    click.echo(pretty_info(res))
