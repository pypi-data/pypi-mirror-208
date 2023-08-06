import click

from .._util.format import pretty_table


@click.command()
@click.pass_obj
def cli(obj: dict):
    """List all buckets in namespace
    """
    client = obj['client']
    namespace = obj['namespace']

    bucket_request = client.bucket.list(namespace=namespace)
    bucket_list = [(bucket['namespace'], bucket['name'], bucket['owner'],
                    '🔒 yes' if bucket['is_encryption_enabled'] == 'true' else '❌ no') for bucket in
                   bucket_request['object_bucket']]
    headers = ['Namespace', 'Bucket Name', 'Owner', 'Encrypted']
    table = pretty_table(bucket_list, headers)
    click.echo(table)
