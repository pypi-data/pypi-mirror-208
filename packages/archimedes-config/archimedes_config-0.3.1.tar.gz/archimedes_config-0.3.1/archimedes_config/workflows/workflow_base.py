"""
Base module for workflows
"""
from archimedes_config.config_manager import ConfigManager
from archimedes_config.keyvault_config_manager import KeyvaultConfigManager


class WorkflowBase:
    """Base class for workflows"""

    def __init__(self):
        self.group_name = None
        try:
            self.conf = KeyvaultConfigManager()
        except ImportError:
            self.conf = ConfigManager()

    def config_has_remote_conn_parameters(self):
        """
        Checks if config can accesss reote key vault
        """
        try:
            self.conf.get("AZURE_KEYVAULT", "VAULT_NAME")
            self.conf.get("AZURE_KEYVAULT", "VAULT_KEY")
        except KeyError:
            return False
        if hasattr(self.conf, "set_default_key_from_key_vault"):
            return True
        return False

    def _get_encrypted(self):
        """Gets encryption status from user"""
        encrypted = input("Do you want the config to be encrypted? [Y/N]: ").lower()
        if encrypted == "y":
            return True
        if encrypted == "n":
            return False
        print("Invalid input!")
        return self._get_encrypted()

    def _get_group_name(self):
        """Gets group name from user"""
        if self.group_name:
            group_name = input(
                f"Enter the group name[Leave empty for `{self.group_name}`]: "
            )
            if group_name:
                self.group_name = group_name
        else:
            self.group_name = input("Enter the group name: ")

        if "." in self.group_name:
            print("Dots are not allowed in group name!")
            self._get_group_name()
        return self.group_name

    def _get_key_name(self):
        """Gets key name from user"""
        key = input("Enter the name for key: ")
        if "." in key:
            print("Dots are not allowed in key name!")
            key = self._get_key_name()
        return key

    def _get_continue_flag(self):
        """Gets continuity flag from user"""
        continue_flag = input("Do you want to add more keys? [Y/N]: ").lower()
        if continue_flag == "y":
            return True
        if continue_flag == "n":
            return False
        print("Invalid input!")
        return self._get_continue_flag()

    def add_single_secret(self):
        """Method to add a single secret to the config"""
        print()
        print("*" * 25)
        self.conf.add_new_config(
            group_name=self._get_group_name(),
            key_name=self._get_key_name(),
            unencrypted_values=input("Enter the plain text value: "),
            encrypted=self._get_encrypted(),
            create_group_if_not_exist=True,
            allow_updating=True,
        )

    def save(self, file_name, save_decrypted=False):
        """Saves the configuration"""
        print()
        print("*" * 25)
        if save_decrypted and self.conf.is_config_encrypted:
            print("Decrypting the configuration...")
            self.conf.decrypt_configs()
        if not self.conf.is_config_encrypted and not save_decrypted:
            print("Encrypting the configuration...")
            self.conf.encrypt_configs()

        print("Saving the configuration...")
        self.conf.save(path=f"{file_name}.toml", allow_saving_decrypted=save_decrypted)
        return file_name

    def load_file(self, file_name):
        """loads config file"""
        self.conf.load(f"{file_name}.toml")

    def _loop_for_secret(self):
        """Loops for addition of secrets to the config"""
        while True:
            self.add_single_secret()
            if not self._get_continue_flag():
                return

    def set_encrypted_key(self, encryption_key=None):
        """Abstract method for setting encrypted key"""
        raise NotImplementedError("`set_encrypted_key` not implemented.")

    def interactive(self, file_name, encryption_key=None):
        """Entry method for interactive flow"""
        self.load_file(file_name)
        self.set_encrypted_key(encryption_key)
        self._loop_for_secret()
        self.save(file_name)
