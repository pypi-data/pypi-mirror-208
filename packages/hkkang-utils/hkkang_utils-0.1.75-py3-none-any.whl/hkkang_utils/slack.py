import os

import attrs
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import hkkang_utils.misc as misc_utils
import hkkang_utils.socket as socket_utils

# Load environment variables
misc_utils.load_dotenv(stack_depth=2)
# Get default access token
DEFAULT_ACCESS_TOKEN = (
    os.environ["SLACK_ACCESS_TOKEN"] if "SLACK_ACCESS_TOKEN" in os.environ else None
)


@attrs.define
class SlackMessenger:
    """Note that the default token is set by the environment variable SLACK_ACCESS_TOKEN."""

    channel: str = attrs.field()
    token: str = attrs.field(default=attrs.Factory(lambda: DEFAULT_ACCESS_TOKEN))
    append_src_info: bool = attrs.field(default=True)

    def __attrs_post_init__(self):
        if self.token is None:
            raise ValueError(
                "Please set token or set SLACK_ACCESS_TOKEN environment variable."
            )

    def send(self, text: str) -> None:
        return send_message(
            token=self.token,
            channel=self.channel,
            text=text,
            append_src_info=self.append_src_info,
        )


def send_message(
    channel: str,
    text: str,
    token: str = DEFAULT_ACCESS_TOKEN,
    append_src_info: bool = True,
) -> None:
    """Please follow the tutorial to get bot OAuthToken and setup the bot permissions.
    https://github.com/slackapi/python-slack-sdk/tree/main/tutorial
    """
    # Check if token is provided
    if token is None:
        raise ValueError(
            "Please set token or set SLACK_ACCESS_TOKEN environment variable."
        )
    # Create client
    client = WebClient(token=token)

    # Build message
    if append_src_info:
        ip = socket_utils.get_local_ip()
        host_name = socket_utils.get_host_name()
        text = f"Message from {host_name}({ip}):\n{text}"

    # Send message
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        assert response["message"]["text"] == text
        print(f"Message sent to channel {channel}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"], "channel_not_found"
        print(f"Got an error: {e.response['error']}")
