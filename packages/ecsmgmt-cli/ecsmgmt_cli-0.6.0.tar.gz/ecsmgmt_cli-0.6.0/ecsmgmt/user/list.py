import click

from .._util.format import pretty_table


@click.command()
@click.pass_obj
def cli(obj: dict):
    """List existing users in namespace
    """
    client = obj['client']
    namespace = obj['namespace']

    user_request = client.object_user.list(namespace=namespace)
    user_list = [(entry['namespace'], entry['userid']) for entry in user_request['blobuser']]
    headers = ['Namespace', 'User ID']
    table = pretty_table(user_list, headers)
    click.echo(table)
