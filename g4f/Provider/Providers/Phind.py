import json
import os
import subprocess
import time

from ...typing import Dict, get_type_hints, sha256

url = "https://phind.com"
model = ["gpt-3.5-turbo", "gpt-4"]
supports_stream = True


def _create_completion(model: str, messages: list, stream: bool, **kwargs):
    path = os.path.dirname(os.path.realpath(__file__))
    config = json.dumps({"model": model, "messages": messages}, separators=(",", ":"))

    cmd = ["python3", f"{path}/helpers/phind.py", config]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in iter(p.stdout.readline, b""):
        if b"<title>Just a moment...</title>" in line:
            os.system("clear" if os.name == "posix" else "cls")
            yield "Clouflare error, please try again..."
            os._exit(0)

        else:
            if b"ping - 2023-" in line:
                continue

            yield line.decode("utf-8")  # [:-1]


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
