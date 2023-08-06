from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import hkkang_utils.socket as socket_utils


def send_message(token: str, channel: str, text: str, append_src_info: bool = True):
    """Please follow the tutorial to get bot OAuthToken and setup the bot permissions.
    https://github.com/slackapi/python-slack-sdk/tree/main/tutorial
    """
    client = WebClient(token=token)

    if append_src_info:
        ip = socket_utils.get_local_ip()
        host_name = socket_utils.get_host_name()
        text = f"Message from {host_name}({ip}):\n{text}"

    try:
        response = client.chat_postMessage(channel=channel, text=text)
        assert response["message"]["text"] == text
        print(f"Message send to the channel {channel}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"], "channel_not_found"
        print(f"Got an error: {e.response['error']}")
