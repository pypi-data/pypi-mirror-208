"""
Utils related to path
"""

import os
import sys
from functools import wraps
from pathlib import Path

from archimedes_config import CLI_COMMAND_NAME


def get_cli_exec_bin_path() -> str:
    """Return path to cli bin executable"""
    pyexec_path = Path(sys.executable)
    return str(pyexec_path.parent / CLI_COMMAND_NAME).replace("\\", "/")


def find_repo_root() -> Path:
    """Finds root directory of repo"""

    current_path = Path(".").absolute().resolve()
    while len(current_path.parents) > 0:
        contents = os.listdir(current_path)
        if ".git" not in contents:
            current_path = current_path.resolve().parent
            continue
        return current_path
    raise Exception("Unable to detect the repo root.")


def resolve_filename_to_base(filename) -> str:
    """Resolved provided local filepath wrt project base"""
    root_path = find_repo_root()

    filename = Path(".").absolute() / filename
    if str(filename).startswith(str(root_path)):
        input_path = filename.relative_to(root_path)
        return str(input_path).replace("\\", "/")
    raise Exception("Config must be set within root path.")


def clean_filename(function):
    """Removes .toml extension out of filename"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Wrapper for cleaning file name"""
        if "file_name" in kwargs:
            if kwargs["file_name"] is not None and kwargs["file_name"].endswith(
                ".toml"
            ):
                kwargs["file_name"] = kwargs["file_name"][:-5]
        return function(*args, **kwargs)

    return wrapper
