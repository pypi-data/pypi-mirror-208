"""
Client for handling interactions with keyvault
"""

import os
from typing import Union

from azure.core.exceptions import ResourceNotFoundError  # pylint:disable=import-error
from azure.identity import (  # pylint:disable=import-error
    DefaultAzureCredential,
    EnvironmentCredential,
)
from azure.keyvault.secrets import SecretClient  # pylint:disable=import-error


class AzureKeyVaultClient:
    """
    Python client to handle communications with Azure keyvault
    """

    def __init__(self, vault_name):
        """
        Init method for KeyVaultClient
        :param vault_name: Name of the vault
        """
        self.credential = self.get_credential()
        self.vault_url = f"https://{vault_name}.vault.azure.net/"
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    @staticmethod
    def get_credential():
        """
        Generates az credentials for authentication

        This method expects
            AZURE_TENANT_ID
            AZURE_CLIENT_ID
            AZURE_CLIENT_SECRET
        set as environments.

        If these are unavailable, az cli login will be used.

        :return:
        """
        if (
            "AZURE_TENANT_ID" in os.environ
            and "AZURE_CLIENT_ID" in os.environ
            and "AZURE_CLIENT_SECRET" in os.environ
        ):
            print("Using environment variables")
            credential = EnvironmentCredential()
        else:
            print("Using default creds")
            credential = DefaultAzureCredential()

        return credential

    def get_secret(
        self, name: str, return_none_if_not_found: bool = True
    ) -> Union[str, None]:
        """
        Retrieves secret for provided name from key vaults


        :param name: Key of secret to import
        :param return_none_if_not_found:
            if true and key not found, returns None
            if false and key not found, raise exception
        :return: Secret
        """

        try:
            secret_value = self.client.get_secret(name.replace("_", "-")).value
            return secret_value
        except ResourceNotFoundError as err:
            if "SecretNotFound" in err.message:
                if return_none_if_not_found:
                    return None
            raise err
