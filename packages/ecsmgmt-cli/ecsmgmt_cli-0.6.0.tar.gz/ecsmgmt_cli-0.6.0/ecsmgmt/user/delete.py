import click
from ecsclient.common.exceptions import ECSClientException

from .._util.echo import success
from .._util.exceptions import EcsmgmtClickException


@click.command()
@click.argument('user-id')
@click.pass_obj
def cli(obj: dict, user_id: str):
    """Delete an object user
    """
    client = obj['client']
    namespace = obj['namespace']

    try:
        client.object_user.delete(user_id=user_id, namespace=namespace)
        success(f'deleted user "{user_id}" in namespace "{namespace}"')
    except ECSClientException as e:
        raise EcsmgmtClickException(e.message)
