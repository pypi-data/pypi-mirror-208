import click
import yaml
from ecsclient.common.exceptions import ECSClientException

from ..._util.echo import success
from ..._util.exceptions import EcsmgmtClickException
from ..._util.format import IndentedListDumper


@click.command()
@click.argument('bucket-name', type=click.STRING)
@click.pass_obj
def cli(obj: dict, bucket_name: str):
    """Set bucket acl

    **This command is only for advanced users!**
    """
    client = obj['client']
    namespace = obj['namespace']

    acl_get = client.bucket.get_acl(bucket_name=bucket_name, namespace=namespace)
    acl_before = acl_get['acl']
    # removing to supported values
    acl_before.pop('default_group_dir_perms')
    acl_before.pop('default_group_file_perms')

    info = """---
# Comments get ignored, save & exit to commit changes
# Reference:
# owner: The name of bucket owner
# default_group: The default group of the bucket
#
# A collection of users and their corresponding permissions
# user_acl:
#   - permission:
#       - full_control
#     user: myuser1
#
# A collection of groups and their corresponding permissions
# group_acl:
#   - permission':
#       - read
#     group: public
#
# A collection of custom groups and their corresponding permissions
# customgroup_acl:
#   - permission:
#       - delete
#       - read
#       - write
#     customgroup: cgroup1

"""

    acl_before_yml = yaml.dump(acl_before, Dumper=IndentedListDumper)
    acl_new = click.edit(f'{info}{acl_before_yml}', extension='yml', require_save=True)

    if acl_new is None:
        click.echo('No changes detected (editor did not save)')
        return

    acl_new_loaded = yaml.safe_load(acl_new)

    if acl_new_loaded == acl_before:
        click.echo('No changes detected')
        return

    try:
        client.bucket.set_acl(bucket_name=bucket_name, namespace=namespace, **acl_new_loaded)
        success(f'Set acls for bucket "{bucket_name}" to:')
        click.echo(yaml.dump(acl_new_loaded, Dumper=IndentedListDumper))
    except ECSClientException as e:
        raise EcsmgmtClickException(e.message)
