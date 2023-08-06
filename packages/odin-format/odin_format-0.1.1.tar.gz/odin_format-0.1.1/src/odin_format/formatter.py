import subprocess
import shlex
from typing import Final

LINE_LENGTH: Final[int] = 79


def call_black(folder_name="."):
    command = shlex.split(f"black --line-length {LINE_LENGTH} {folder_name}")

    subprocess.run(command, shell=False)
