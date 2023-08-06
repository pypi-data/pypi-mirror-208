import logging

import click

import slack_primitive_cli
from slack_primitive_cli.command import chat, files

logging.basicConfig(level=logging.DEBUG)


@click.group()
@click.version_option(version=slack_primitive_cli.__version__)
def cli():
    pass


cli.add_command(chat.delete)
cli.add_command(chat.postMessage)
cli.add_command(files.delete)
cli.add_command(files.upload)

if __name__ == "__main__":
    cli()
