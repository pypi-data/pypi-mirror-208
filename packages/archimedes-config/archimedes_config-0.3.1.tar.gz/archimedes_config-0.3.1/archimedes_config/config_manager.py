"""
Class declaration for configuration manager
"""
from copy import deepcopy
from typing import Any, Dict, Union

import tomlkit
from cryptography.fernet import Fernet
from tomlkit.items import Bool, Float, Integer, Null, String


class ConfigManager:
    """
    Manages Configurations
    """

    def __init__(
        self, path: str = None, default_key=None, decrypt_on_load: bool = False
    ) -> None:
        """Init for configuration handler

        Arguments:
            path (str|path): Path to the config file
            default_key (str): Default configuration key to use for encryption / decryption
            decrypt_on_load (bool): Decrypt the config on load
        """
        self._configs = None  # Loaded config
        self.config_loaded_from = (
            None  # Path config loaded from. Used as default saving location.
        )
        self._default_key = None  # Default key

        # if path, set load the config
        if path:
            self.load(path=path)

        # if default key is set, set the key
        if default_key:
            self.set_default_key(default_key)

        if decrypt_on_load and self.is_config_encrypted:
            self.decrypt_configs()

    def __repr__(self) -> str:
        """
        Shows state of configs
        Encrypted configs will not be print encrypted

        :return:
        """
        print_data = {}
        for group, keys in self.config.items():
            print_data[group] = {}
            for key, data in keys.items():
                print_data[group][key] = {}
                for field, value in data.items():
                    print_data[group][key][field] = (
                        "***ENCRYPTED***"
                        if (
                            field == "value"
                            and data.get("encrypted", False)
                            and not self.is_config_encrypted
                        )
                        else value
                    )
        print_data = self.format_toml(print_data)
        return print_data

    @property
    def is_config_encrypted(self) -> bool:
        """Checks the state of encryption if configuration"""
        return self.config["CONFIGURATIONS"]["_IS_CONFIG_ENCRYPTED"]["value"]

    @property
    def default_key(self) -> str:
        """Returns remote key in AZ key vault"""
        if not self._default_key:
            raise ValueError("Default key has not been set.")
        return self._default_key

    @property
    def config(self) -> tomlkit.TOMLDocument:
        """Returns configuration"""
        if self._configs:
            return self._configs
        raise ValueError("Configuration has not been loaded.")

    def set_default_key(self, key: str):
        """Sets a default key"""

        if self._default_key:
            raise ValueError("Default key has already been set.")
        self._default_key = key

    def format_toml(self, toml_data: Dict = None):
        """
        Formats input toml into pretty format
        :param toml_data: Dict representation of toml
        :return:
        """
        if toml_data is None:
            toml_data = self.config
        return tomlkit.dumps(toml_data)

    def get(self, group: str, item: str, *, default_return=KeyError) -> Any:
        """
        Returns value for the key
        :param group: Name of group the key belongs to
        :param item: Name of key to extract
        :param default_return: Returns this value if key does not exist in configuration
        :return:
        """
        try:
            key_meta = self.config[group][item]
        except KeyError as err:
            if default_return == KeyError:
                raise err
            return default_return
        if key_meta.get("encrypted", False) and self.is_config_encrypted:
            raise ValueError("Configuration has not been decrypted.")
        value = self.config[group][item]["value"]

        # Ensure that derived classes are on the starting of the mapping dict
        method_mapping = {
            Null: None,
            String: str,
            str: str,
            Bool: bool,
            bool: bool,
            Float: float,
            float: float,
            Integer: int,
            int: int,
        }
        for value_type, fn_cast in method_mapping.items():
            if isinstance(value, value_type):
                return None if fn_cast is None else fn_cast(value)
        raise NotImplementedError(f"Parsing for {type(value)} not supported.")

    def _encrypt_value(self, encrypted: bool, value: Any, key: str = None):
        """
        Encrypts a single value
        :param encrypted: If true, encrypts
        :param value: value to encrypt
        :param key:
        :return:
        """
        key = key if key else self.default_key
        if encrypted:
            value = Fernet(key).encrypt(value.encode()).decode()
        return value

    def _decrypt_value(self, encrypted: bool, value, key: str = None):
        """
        Decrypts a value
        :param encrypted: If true decrypts
        :param value: Valur to decrypt
        :return:
        """
        key = key if key else self.default_key
        if encrypted:
            value = Fernet(key).decrypt(value).decode()
        return value

    def save(self, path: str = None, allow_saving_decrypted: bool = False) -> None:
        """
        Save configuration into a toml file
        :param path:
            Path to save the configs to
            Defaults to the path the configs were loaded from
        :param allow_saving_decrypted:
            If true, allows saving decrypted configs
        :return:
        """
        if not self.is_config_encrypted:
            if not allow_saving_decrypted:
                raise ValueError(
                    "Saving decrypted configs is not allowed."
                    "Set `allow_saving_decrypted` to True to save decrypted configs."
                )
        if path is None:
            if not self.config_loaded_from:
                raise ValueError("Both default path and specific path not set.")
            path = self.config_loaded_from

        formatted_toml = self.format_toml()
        with open(path, "w", encoding="utf8") as file:
            file.write(formatted_toml)

    def create(self):
        """
        Initializes a new unencrypted configuration
        """
        if self._configs:
            raise ValueError("Configuration has already been loaded.")

        encryption_table = tomlkit.table(False)
        encryption_table.append("value", False)

        configuration_table = tomlkit.table(False)
        configuration_table.append("_IS_CONFIG_ENCRYPTED", encryption_table)

        configs = tomlkit.document()
        configs.append("CONFIGURATIONS", configuration_table)
        self._configs = configs

    def load(self, path="config.toml"):
        """
        Loads an environment toml file
        :param path: path to the toml file to read configs from
        :return:
        """
        if self._configs:
            raise ValueError("Configuration has already been loaded.")
        self.config_loaded_from = path
        with open(path, "r", encoding="utf8") as file:
            config = tomlkit.load(file)
        config_copy = deepcopy(config)
        for grp, keys in config.items():
            for field, content in keys.items():
                if "encrypted" in content and not content["encrypted"]:
                    del config_copy[grp][field]["encrypted"]

                if "value" not in content:
                    raise ValueError(
                        f"Invalid toml file. " f"Header {field} doesnt have `value`."
                    )

        self._configs = config_copy

    def list_groups(self):
        """Returns groups"""
        return list(self.config.keys())

    def list_keys(self, group: str):
        """Returns list of keys in configuration"""
        return list(self.config[group].keys())

    def create_new_key(
        self,
        config_save_path: str,
        key_save_path: str,
    ):
        """
        Encrypts an existing toml with a new key

        :param config_save_path: Path to store new config
        :param key_save_path: Path to store new key
        :return:
        """
        new_key = Fernet.generate_key()
        config_encryption_state = self.is_config_encrypted
        if config_encryption_state:
            self.decrypt_configs()
        new_config = self.encrypt_configs(key=new_key.decode(), inplace=False)
        if config_encryption_state:  # revert configuration state to previous
            self.encrypt_configs()

        new_config = self.format_toml(new_config)
        with open(config_save_path, "w", encoding="utf8") as file:
            file.write(new_config)
        with open(key_save_path, "w", encoding="utf8") as file:
            file.write(new_key.decode())

    def encrypt_configs(self, key: str = None, inplace=True) -> Union[Dict, None]:
        """
        Encrypts all the configs
        :param key:
            Key to use for encryption
            Defaults to key set in registry
        :param inplace:
            If true, modifies in memory and returns none
            If false, returns modified data
        :return:
        """
        if self.is_config_encrypted:
            raise ValueError("Config has already been encrypted.")
        key = key if key else self.default_key

        new_encrypted_config = deepcopy(self.config)
        for group, keys in self.config.items():
            for config_key, value in keys.items():
                value = self._encrypt_value(
                    value.get("encrypted", False), value["value"], key
                )
                new_encrypted_config[group][config_key]["value"] = value
        if not inplace:
            return new_encrypted_config
        self._configs = new_encrypted_config
        self._configs["CONFIGURATIONS"]["_IS_CONFIG_ENCRYPTED"]["value"] = True
        return None

    def decrypt_configs(self, bypass_key: str = None, inplace: bool = True):
        """
        Decrypts an env file
        :param bypass_key: If provided, ignores the key in azure registry
        :param inplace:
            If true, modifies in memory and returns none
            If false, returns modified data
        :return:
        """
        if not self.is_config_encrypted:
            raise ValueError("Keys have already been decrypted.")
        enc_key = bypass_key if bypass_key else self.default_key

        decoded_config = deepcopy(self.config)
        for group, keys in self.config.items():
            for key, value in keys.items():
                decoded_config[group][key]["value"] = self._decrypt_value(
                    value.get("encrypted", False), value["value"], enc_key
                )
        if not inplace:
            return decoded_config
        self._configs = decoded_config
        self._configs["CONFIGURATIONS"]["_IS_CONFIG_ENCRYPTED"]["value"] = False
        return None

    def add_new_config(  # pylint:disable=too-many-arguments,too-many-branches
        self,
        group_name: str,
        key_name: str,
        unencrypted_values: Any,
        encrypted: bool,
        create_group_if_not_exist: bool = False,
        allow_updating: bool = False,
    ):
        """
        Adds a new configuration

        :param group_name: Group Name that configuration belongs to
        :param key_name: Name for configuration
        :param unencrypted_values: Value to store
        :param encrypted: If true, encrypts the value
        :param create_group_if_not_exist: If false, if group name does not exist raises exception
        :param allow_updating: If false, attempting to update existing key will raise an issue
        :return:
        """
        if "." in group_name:
            raise ValueError("Group name cannot have dot `.`")
        if "." in key_name:
            raise ValueError("Key name cannot have dot `.`")

        if encrypted and self.is_config_encrypted:
            value = self._encrypt_value(True, unencrypted_values)
        else:
            value = unencrypted_values

        if group_name not in self.config:
            if not create_group_if_not_exist:
                raise ValueError(
                    f"Group `{group_name}` doesnt exists."
                    f"Creation of group is not allowed."
                )
            key_table = tomlkit.table(False)
            key_table.append("value", value)
            if encrypted:
                key_table.append("encrypted", encrypted)

            group_table = tomlkit.table(False)
            group_table.append(key_name, key_table)
            self.config.append(group_name, group_table)
            return
        if not allow_updating:
            if key_name in self.config[group_name]:
                raise ValueError(
                    f"{key_name} already exists in config." f" Updating is not allowed."
                )
        if key_name in self.config[group_name]:
            self.config[group_name][key_name]["value"] = value
            if encrypted:
                self.config[group_name][key_name]["encrypted"] = encrypted
        else:
            key_table = tomlkit.table(False)
            key_table.append("value", value)
            if encrypted:
                key_table.append("encrypted", encrypted)
            self.config[group_name].append(key_name, key_table)


if __name__ == "__main__":
    a = ConfigManager("../a.toml")
    print(type(a.get("a", "a")))
