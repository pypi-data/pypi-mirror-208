import logging

import click
import slack_sdk

from slack_primitive_cli.common.utils import TOKEN_ENVVAR, TOKEN_HELP_MESSAGE, set_logger

logger = logging.getLogger(__name__)


@click.command(
    name="chat.postMessage", help="Sends a message to a channel. See https://api.slack.com/methods/chat.postMessage "
)
@click.option("--token", envvar=TOKEN_ENVVAR, required=True, help=TOKEN_HELP_MESSAGE)
@click.option(
    "--channel",
    required=True,
    help="Channel, private group, or IM channel to send message to. "
    "Can be an encoded ID, or a name. See below for more details.",
)
@click.option(
    "--text",
    required=True,
    help="How this field works and whether it is required depends on other fields you use in your API call.",
)
@click.option("--as_user", type=bool, help="Pass true to post the message as the authed user, instead of as a bot.")
@click.option("--attachments", help="A JSON-based array of structured attachments, presented as a URL-encoded string.")
@click.option("--blocks", help="A JSON-based array of structured blocks, presented as a URL-encoded string.")
@click.option(
    "--icon_emoji",
    help="Emoji to use as the icon for this message. Overrides icon_url. "
    "Must be used in conjunction with as_user set to false, otherwise ignored. See authorship below.",
)
@click.option(
    "--icon_url",
    help="URL to an image to use as the icon for this message. "
    "Must be used in conjunction with as_user set to false, otherwise ignored. See authorship below.",
)
@click.option("--link_names", type=bool, help="Find and link channel names and usernames.")
@click.option("--mrkdwn", type=bool, help="Disable Slack markup parsing by setting to false.")
@click.option("--parse", type=bool, help="Change how messages are treated.")
@click.option(
    "--reply_broadcast",
    type=bool,
    help="Used in conjunction with thread_ts and indicates "
    "whether reply should be made visible to everyone in the channel or conversation.",
)
@click.option(
    "--thread_ts",
    help="Provide another message's ts value to make this message a reply. "
    "Avoid using a reply's ts value; use its parent instead.",
)
@click.option("--unfurl_links", type=bool, help="Pass true to enable unfurling of primarily text-based content.")
@click.option("--unfurl_media", type=bool, help="Pass false to disable unfurling of media content.")
@click.option(
    "--username",
    help="Set your bot's user name. Must be used in conjunction with as_user set to false, otherwise ignored.",
)
def postMessage(
    token: str,
    channel: str,
    text: str,
    as_user,
    attachments,
    blocks,
    icon_emoji,
    icon_url,
    link_names,
    mrkdwn,
    parse,
    reply_broadcast,
    thread_ts,
    unfurl_links,
    unfurl_media,
    username,
):
    set_logger()
    client = slack_sdk.WebClient(token=token)
    response = client.chat_postMessage(
        channel=channel,
        text=text,
        as_user=as_user,
        attachments=attachments,
        blocks=blocks,
        icon_emoji=icon_emoji,
        icon_url=icon_url,
        link_names=link_names,
        mrkdwn=mrkdwn,
        parse=parse,
        reply_broadcast=reply_broadcast,
        thread_ts=thread_ts,
        unfurl_links=unfurl_links,
        unfurl_media=unfurl_media,
        username=username,
    )
    print(response)
    return response


@click.command(name="chat.delete", help="Deletes a message. See https://api.slack.com/methods/chat.delete ")
@click.option("--token", envvar=TOKEN_ENVVAR, required=True, help=TOKEN_HELP_MESSAGE)
@click.option("--channel", required=True, help="Channel containing the message to be deleted.")
@click.option("--ts", required=True, help="Timestamp of the message to be deleted.")
@click.option(
    "--as_user",
    type=bool,
    help="Pass true to delete the message as the authed user with chat:write:user scope. "
    "Bot users in this context are considered authed users. "
    "If unused or false, the message will be deleted with chat:write:bot scope.",
)
def delete(token: str, channel: str, ts: str, as_user):
    set_logger()
    client = slack_sdk.WebClient(token=token)
    response = client.chat_delete(channel=channel, ts=ts, as_user=as_user)
    print(response)
    return response
