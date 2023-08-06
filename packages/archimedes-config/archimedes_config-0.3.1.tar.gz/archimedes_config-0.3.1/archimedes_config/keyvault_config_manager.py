"""
Module for configurations and az vault secrets
"""

import logging

from archimedes_config.config_manager import ConfigManager

try:
    from archimedes_config.keyvault_client import AzureKeyVaultClient
except ImportError as err:
    AzureKeyVaultClient = None


class KeyvaultConfigManager(ConfigManager):  # pylint:disable=too-few-public-methods
    """Class for configurations and az vault secrets"""

    def __init__(
        self, path: str = None, default_key=None, decrypt_on_load: bool = False
    ):
        if AzureKeyVaultClient is None:
            error_message = (
                "Environment has not been setup to handle interactions with Key Vault."
            )
            logging.critical(error_message)
            raise ImportError(error_message)

        super().__init__(
            path=path, default_key=default_key, decrypt_on_load=decrypt_on_load
        )

    def set_default_key_from_key_vault(self):
        """Set default key using secret saved in Azure Key Vault"""

        vault_name = self.config["AZURE_KEYVAULT"]["VAULT_NAME"]["value"]
        key_name = self.config["AZURE_KEYVAULT"]["VAULT_KEY"]["value"]

        self.set_default_key(AzureKeyVaultClient(vault_name).get_secret(name=key_name))
