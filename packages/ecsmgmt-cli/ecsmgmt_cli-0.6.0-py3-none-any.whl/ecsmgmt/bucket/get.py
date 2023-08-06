import click

from .._util.format import pretty_info


@click.command()
@click.argument('bucket-name', type=click.STRING)
@click.pass_obj
def cli(obj: dict, bucket_name: str):
    """Get bucket details
    """
    client = obj['client']
    namespace = obj['namespace']

    res = client.bucket.get(bucket_name=bucket_name, namespace=namespace)

    click.secho(f'Bucket "{bucket_name}" info:', bold=True)
    click.echo(pretty_info(res))
