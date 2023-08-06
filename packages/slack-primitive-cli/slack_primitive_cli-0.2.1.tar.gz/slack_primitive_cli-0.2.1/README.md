# slack-primitive-cli
[![Build Status](https://travis-ci.org/yuji38kwmt/slack-primitive-cli.svg?branch=master)](https://travis-ci.org/yuji38kwmt/slack-primitive-cli)
[![PyPI version](https://badge.fury.io/py/slack-primitive-cli.svg)](https://badge.fury.io/py/slack-primitive-cli)
[![Python Versions](https://img.shields.io/pypi/pyversions/slack-primitive-cli.svg)](https://pypi.org/project/slack-primitive-cli/)

`slack-primitive-cli` can execute [Slack web api methods](https://api.slack.com/methods) from command line.
Command line argument is correspont to web api arguments, so `slack-primitive-cli` is **primitive**.


# Requirements
* Python 3.7+

# Install

```
$ pip install slack-primitive-cli
```

https://pypi.org/project/slack-primitive-cli/


# Usage

## Sending a message

```
$ slackcli chat.postMessage --token xoxb-XXXXXXX --channel "#random" --text hello

$ export SLACK_API_TOKEN=xoxb-XXXXXXX
$ slackcli chat.postMessage  --channel "#random" --text hello
```


```
$ slackcli chat.postMessage --help

Usage: slackcli chat.postMessage [OPTIONS]

  Sends a message to a channel. See
  https://api.slack.com/methods/chat.postMessage

Options:
  --token TEXT               Authentication token. If not specified, refer
                             `SLACK_API_TOKEN` environment variable.
                             [required]

  --channel TEXT             Channel, private group, or IM channel to send
                             message to. Can be an encoded ID, or a name. See
                             below for more details.  [required]

  --text TEXT                How this field works and whether it is required
                             depends on other fields you use in your API call.
                             [required]

  --as_user BOOLEAN          Pass true to post the message as the authed user,
                             instead of as a bot.

  --attachments TEXT         A JSON-based array of structured attachments,
                             presented as a URL-encoded string.

  --blocks TEXT              A JSON-based array of structured blocks,
                             presented as a URL-encoded string.

  --icon_emoji TEXT          Emoji to use as the icon for this message.
                             Overrides icon_url. Must be used in conjunction
                             with as_user set to false, otherwise ignored. See
                             authorship below.

  --icon_url TEXT            URL to an image to use as the icon for this
                             message. Must be used in conjunction with as_user
                             set to false, otherwise ignored. See authorship
                             below.

  --link_names BOOLEAN       Find and link channel names and usernames.
  --mrkdwn BOOLEAN           Disable Slack markup parsing by setting to false.
  --parse BOOLEAN            Change how messages are treated.
  --reply_broadcast BOOLEAN  Used in conjunction with thread_ts and indicates
                             whether reply should be made visible to everyone
                             in the channel or conversation.

  --thread_ts TEXT           Provide another message's ts value to make this
                             message a reply. Avoid using a reply's ts value;
                             use its parent instead.

  --unfurl_links BOOLEAN     Pass true to enable unfurling of primarily text-
                             based content.

  --unfurl_media BOOLEAN     Pass false to disable unfurling of media content.
  --username TEXT            Set your bot's user name. Must be used in
                             conjunction with as_user set to false, otherwise
                             ignored.

  --help                     Show this message and exit.

```
## Uploading files

```
$ slackcli files.upload --channels "#random" --file foo.txt
```

```
$ slackcli files.upload  --help
Usage: slackcli files.upload [OPTIONS]

  Uploads or creates a file. See https://api.slack.com/methods/files.upload

Options:
  --token TEXT                    Authentication token. If not specified,
                                  refer `SLACK_API_TOKEN` environment
                                  variable.  [required]

  --channels TEXT                 Comma-separated list of channel names or IDs
                                  where the file will be shared.  [required]

  File contents: [mutually_exclusive, required]
    --file TEXT                   File contents via multipart/form-data. If
                                  omitting this parameter, you must submit
                                  content.

    --content TEXT                File contents via a POST variable. If
                                  omitting this parameter, you must provide a
                                  file.

  --filename TEXT                 Filename of file.
  --filetype TEXT                 A file type identifier. See also
                                  https://api.slack.com/types/file#file_types
                                  .

  --initial_comment TEXT          The message text introducing the file in
                                  specified channels.

  --thread_ts TEXT                Provide another message's ts value to upload
                                  this file as a reply.

  --title TEXT                    Title of file.

```

# Supported web api methods.
`slack-primitive-cli` supports a few web api methods.

* [chat.delete](https://api.slack.com/methods/chat.delete)
* [chat.postMessage](https://api.slack.com/methods/chat.postMessage)
* [files.delete](https://api.slack.com/methods/files.delete)
* [files.upload](https://api.slack.com/methods/files.upload)

# Additional

## Shell Completion
`slack-primitive-cli` depends on [click](https://click.palletsprojects.com/en/7.x/), so `slack-primitive-cli` can provide tab completion.
Bash, Zsh, and Fish are supported

In order to activate shell completion, you need to execute the following script.

```
$ eval "$(_SLACKCLI_COMPLETE=source slackcli)"
```


See [here](https://click.palletsprojects.com/en/7.x/bashcomplete/) for details.

