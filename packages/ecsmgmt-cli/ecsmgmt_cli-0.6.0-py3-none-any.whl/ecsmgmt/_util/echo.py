import click


def success(message: str):
    click.secho('Success: ', nl=False, fg='green', bold=True)
    click.echo(message)
