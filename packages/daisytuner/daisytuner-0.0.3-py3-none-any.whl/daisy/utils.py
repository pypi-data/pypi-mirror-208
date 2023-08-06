import os
import socket

from pathlib import Path


def global_cache():
    if "DAISY_GLOBAL_CACHE" in os.environ:
        return Path(os.environ["DAISY_GLOBAL_CACHE"])
    return Path.home() / ".daisy"


def host():
    return socket.gethostname()
