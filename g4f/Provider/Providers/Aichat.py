import os

import requests

from ...typing import Dict, get_type_hints, sha256

url = "https://chat-gpt.org/chat"
model = ["gpt-3.5-turbo"]
supports_stream = False


def _create_completion(model: str, messages: list, stream: bool, **kwargs):
    headers = {
        "authority": "chat-gpt.org",
        "accept": "*/*",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://chat-gpt.org",
        "pragma": "no-cache",
        "referer": "https://chat-gpt.org/chat",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    json_data = {
        "message": messages[-1]["content"],
        "temperature": 1,
        "presence_penalty": 0,
        "top_p": 1,
        "frequency_penalty": 0,
    }

    response = requests.post(
        "https://chat-gpt.org/api/text", headers=headers, json=json_data
    )
    yield response.json()["message"]


params = (
    f"g4f.Providers.{os.path.basename(__file__)[:-3]} supports: "
    + "(%s)"
    % ", ".join(
        [
            f"{name}: {get_type_hints(_create_completion)[name].__name__}"
            for name in _create_completion.__code__.co_varnames[
                : _create_completion.__code__.co_argcount
            ]
        ]
    )
)
