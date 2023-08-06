import click
from ecsclient.common.exceptions import ECSClientException

from ..._util import types
from ..._util.echo import success
from ..._util.exceptions import EcsmgmtClickException


@click.command()
@click.argument('bucket-name', type=click.STRING)
@click.argument('period', type=types.TIME)
@click.pass_obj
def cli(obj: dict, bucket_name: str, period: int):
    """Set bucket retention
    """
    client = obj['client']
    namespace = obj['namespace']

    try:
        client.bucket.set_retention(bucket_name=bucket_name, namespace=namespace, period=period)
        success(f'Set retention for bucket "{bucket_name}" to {period} seconds')
    except ECSClientException as e:
        raise EcsmgmtClickException(e.message)
