import logging
import os

import click
import slack_sdk
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup

from slack_primitive_cli.common.utils import TOKEN_ENVVAR, TOKEN_HELP_MESSAGE, my_backoff, set_logger

logger = logging.getLogger(__name__)


@click.command(name="files.upload", help="Uploads or creates a file. See https://api.slack.com/methods/files.upload ")
@click.option("--token", envvar=TOKEN_ENVVAR, required=True, help=TOKEN_HELP_MESSAGE)
@click.option(
    "--channels", required=True, help="Comma-separated list of channel names or IDs where the file will be shared."
)
@optgroup.group("File contents", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option(
    "--file", help="File contents via multipart/form-data. If omitting this parameter, you must submit content."
)
@optgroup.option(
    "--content", help="File contents via a POST variable. If omitting this parameter, you must provide a file."
)
@click.option("--filename", help="Filename of file.")
@click.option("--filetype", help="A file type identifier. See also https://api.slack.com/types/file#file_types .")
@click.option("--initial_comment", help="The message text introducing the file in specified channels.")
@click.option("--thread_ts", help="Provide another message's ts value to upload this file as a reply.")
@click.option("--title", help="Title of file.")
@my_backoff
def upload(token, channels, file, content, filename, filetype, initial_comment, thread_ts, title):
    set_logger()
    client = slack_sdk.WebClient(token=token)

    if filename is None and file is not None:
        filename = os.path.basename(file)

    response = client.files_upload(
        channels=channels,
        file=file,
        content=content,
        filename=filename,
        filetype=filetype,
        initial_comment=initial_comment,
        thread_ts=thread_ts,
        title=title,
    )
    print(response)
    return response


@click.command(name="files.delete", help="Deletes a file. See https://api.slack.com/methods/files.delete ")
@click.option("--token", envvar=TOKEN_ENVVAR, required=True, help=TOKEN_HELP_MESSAGE)
@click.option("--file", required=True, help="ID of file to delete.")
@my_backoff
def delete(token, file):
    set_logger()
    client = slack_sdk.WebClient(token=token)
    response = client.files_delete(file=file)
    print(response)
    return response
