import click
from ecsclient.common.exceptions import ECSClientException

from .._util.echo import success
from .._util.exceptions import EcsmgmtClickException


@click.command()
@click.argument('user-id', type=click.STRING)
@click.option(
    '-t', '--tag', 'tags',
    multiple=True,
    type=click.STRING,
    help='User tags seperated by ",", option can be provided multiple times'
)
@click.pass_obj
def cli(obj: dict, user_id: str, tags: list[str]):
    """Create new object user
    """
    client = obj['client']
    namespace = obj['namespace']

    sane_tags = []
    for tag in tags:
        splited = tag.split(',')
        sane_tags.extend(splited)

    try:
        client.object_user.create(user_id=user_id, namespace=namespace, tags=sane_tags)
        success(f'created user "{user_id}" in namespace "{namespace}"')
    except ECSClientException as e:
        raise EcsmgmtClickException(e.message)
