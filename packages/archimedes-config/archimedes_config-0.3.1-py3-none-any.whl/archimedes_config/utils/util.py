"""
Utils related to config
"""

import subprocess
from typing import Any, List

import tomlkit

from archimedes_config.config_manager import ConfigManager
from archimedes_config.utils.path_utils import find_repo_root, resolve_filename_to_base


class RegisteredConfigDecrypted(Exception):
    """Exception to be raised when all the registered config ar enot encrypted"""


def get_secret(file_name, secret_path, *, default_return: Any = KeyError) -> Any:
    """Retrieves secret key from registry"""
    file_name = resolve_filename_to_base(file_name)

    with open(secret_path, "r", encoding="utf8") as file:
        secrets = tomlkit.load(file)
    try:
        return secrets[file_name]
    except KeyError as err:
        if default_return is KeyError:
            raise err
        return default_return


def register_secret(file_name, secret_path, secret_key) -> None:
    """Registers secret key to registry"""
    print("Registering newly generated encryption key...")
    file_name = resolve_filename_to_base(file_name)

    with open(secret_path, "r", encoding="utf8") as file:
        secrets = tomlkit.load(file)
    secrets.add(file_name, secret_key)

    with open(secret_path, "w", encoding="utf8") as file:
        tomlkit.dump(secrets, file)


def register_config(file_name, config_path) -> None:
    """Registers config to pre commit registry"""
    file_name = resolve_filename_to_base(file_name)
    with open(config_path, "r", encoding="utf8") as file:
        config = tomlkit.load(file)
    if file_name not in config["registered_configs"]:
        config["registered_configs"].append(file_name)  # pylint:disable=no-member
        with open(config_path, "w", encoding="utf8") as file:
            tomlkit.dump(config, file)
    else:
        print("Config already registered.")


def unregister_config(file_name, config_path) -> None:
    """Unregisters config from pre commit registry"""

    with open(config_path, "r", encoding="utf8") as file:
        config = tomlkit.load(file)

    file_name = resolve_filename_to_base(file_name)
    if file_name in config["registered_configs"]:
        config["registered_configs"] = [
            i for i in config["registered_configs"] if i != file_name
        ]
    else:
        raise Exception("Provided config was never registered.")
    with open(config_path, "w", encoding="utf8") as file:
        tomlkit.dump(config, file)


def get_registered_configs(config_path) -> List[str]:
    """Returns all the registered configuration sets"""
    with open(config_path, "r", encoding="utf8") as file:
        configs = tomlkit.load(file)
    return configs["registered_configs"]


def check_encrypted(config_path) -> None:
    """Checks if all registered configs are encrypted"""

    root_path = find_repo_root()
    configs = get_registered_configs(config_path)

    committed_files = (
        subprocess.check_output("git diff --name-only --cached".split(" "))
        .decode()
        .split("\n")
    )
    committed_files = [f"{i[:-5]}" for i in committed_files if i.endswith(".toml")]
    committed_files = list(set(configs).intersection(set(committed_files)))
    if len(committed_files) == 0:
        print("Commit doesnt include registered config. Commit is safe.")
        return
    issues = {}
    for config in configs:
        config = root_path / f"{config}.toml"
        try:
            _c = ConfigManager(path=str(config))
        except (FileNotFoundError, IsADirectoryError):
            issues[config] = "FileNotFound"
        else:
            if not _c.get("CONFIGURATIONS", "_IS_CONFIG_ENCRYPTED"):
                issues[config] = "Decrypted"
    if issues:
        issues = "".join(f"\n\t{path} [{issue}]" for path, issue in issues.items())
        issues = f"Issues with config(s) detected: {issues}"
        raise RegisteredConfigDecrypted(issues)
    print("All configurations are encrypted.")
