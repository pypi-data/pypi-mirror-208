import click
from ecsclient.common.exceptions import ECSClientException

from .._util.echo import success
from .._util.exceptions import EcsmgmtClickException


@click.command()
@click.argument('bucket-name', type=click.STRING)
@click.pass_obj
def cli(obj: dict, bucket_name: str):
    """Delete bucket
    """
    client = obj['client']
    namespace = obj['namespace']

    try:
        client.bucket.delete(bucket_name=bucket_name, namespace=namespace)
        success(f'deleted bucket "{bucket_name}" in namespace "{namespace}"')
    except ECSClientException as e:
        raise EcsmgmtClickException(e.message)
