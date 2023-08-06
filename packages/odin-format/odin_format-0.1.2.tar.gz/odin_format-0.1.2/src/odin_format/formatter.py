"""Formatter for code functions."""
import argparse
import contextlib
import shlex
import subprocess
from typing import Final

LINE_LENGTH: Final[int] = 79


def format():
    """Format the code.

    :return:
    """
    parser = argparse.ArgumentParser(description="Odinnnn")
    parser.add_argument("folder", type=str, help="the folder to format")
    parser.add_argument("--end", dest="end", default="!", help="Others")
    args = parser.parse_args()
    format_code(args.folder)


def format_code(folder_name="."):
    """Format the code.

    :param folder_name:
    """
    isort_command = shlex.split(f"isort --profile black {folder_name}")
    black_command = shlex.split(
        f"black --line-length {LINE_LENGTH} {folder_name}"
    )
    docformatter = shlex.split(f"docformatter -ir {folder_name}")

    for command in [isort_command, black_command, docformatter]:
        with contextlib.suppress(subprocess.CalledProcessError):
            subprocess.run(command, shell=False, check=True)


def lint_code(folder_name="."):
    """Lint the code.

    :param folder_name:
    """
    pylint_command = shlex.split(f"pylint --recursive=y {folder_name}")
    flake8_command = shlex.split(f"flake8 {folder_name}")
    pydocstyle_command = shlex.split(f"pydocstyle {folder_name}")
    docformatter = shlex.split(f"docformatter -cr {folder_name} ")

    for command in [
        pylint_command,
        flake8_command,
        pydocstyle_command,
        docformatter,
    ]:
        with contextlib.suppress(subprocess.CalledProcessError):
            subprocess.run(command, shell=False, check=True)
