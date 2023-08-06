import functools
import logging
import socket
from urllib.error import URLError

import backoff
from slack_sdk.errors import SlackClientError

TOKEN_ENVVAR = "SLACK_API_TOKEN"
TOKEN_HELP_MESSAGE = f"Authentication token. If not specified, refer `{TOKEN_ENVVAR}` environment variable."


def set_logger():
    logging_formatter = "%(levelname)-8s : %(asctime)s : %(filename)s : %(name)s : %(funcName)s : %(message)s"
    logging.basicConfig(format=logging_formatter)
    logging.getLogger("slack_primitive_cli").setLevel(level=logging.DEBUG)


def my_backoff(function):
    """
    タイムアウトが発生したときにリトライする. 最大5分間リトライする。
    """

    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        def fatal_code(e):
            if isinstance(e, socket.timeout):
                return False
            elif isinstance(e, URLError):
                return False
            else:
                return True

        return backoff.on_exception(
            backoff.expo,
            (socket.timeout, URLError, SlackClientError),
            jitter=backoff.full_jitter,
            max_time=300,
            giveup=fatal_code,
        )(function)(*args, **kwargs)

    return wrapped
