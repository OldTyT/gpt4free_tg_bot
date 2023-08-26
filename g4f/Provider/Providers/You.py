import json
import os
import subprocess
import time

from ...typing import Dict, get_type_hints, sha256

url = "https://you.com"
model = "gpt-3.5-turbo"
supports_stream = True


def _create_completion(model: str, messages: list, stream: bool, **kwargs):
    path = os.path.dirname(os.path.realpath(__file__))
    config = json.dumps({"messages": messages}, separators=(",", ":"))

    cmd = ["python3", f"{path}/helpers/you.py", config]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in iter(p.stdout.readline, b""):
        yield line.decode("utf-8")  # [:-1]
