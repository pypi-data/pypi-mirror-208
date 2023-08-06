"""
Workflow to create a new secret
"""

from cryptography.fernet import Fernet

from archimedes_config.workflows.workflow_base import WorkflowBase


class ConfigCreator(WorkflowBase):
    """Class for creating secret"""

    def __init__(self):
        super().__init__()
        self.new_key_generated = True

    def load_file(self, file_name):
        """Creates a new config"""
        self.conf.create()

    def set_encrypted_key(self, encryption_key=None):
        """Creates a new encryption key"""
        while True:
            option = input(
                "Do you want to \n"
                "- generate a new encryption key or [N]\n"
                "- add a key from Azure KeyVault [C]?\n"
                "Enter N or C: "
            ).lower()
            if option == "n":
                self.conf.set_default_key(Fernet.generate_key().decode())
            elif option == "c":
                if not hasattr(self.conf, "set_default_key_from_key_vault"):
                    raise ImportError(
                        "Environment has not been configured to handle connections with azure key vault."
                    )
                self.new_key_generated = False
                vault_name = input("Enter vault name: ")
                self.conf.add_new_config(
                    group_name="AZURE_KEYVAULT",
                    key_name="VAULT_NAME",
                    encrypted=False,
                    unencrypted_values=vault_name,
                    create_group_if_not_exist=True,
                    allow_updating=True,
                )
                vault_key = input("Enter vault key: ")

                self.conf.add_new_config(
                    group_name="AZURE_KEYVAULT",
                    key_name="VAULT_KEY",
                    encrypted=False,
                    unencrypted_values=vault_key,
                    create_group_if_not_exist=True,
                    allow_updating=True,
                )
                self.conf.set_default_key_from_key_vault()
            else:
                print("Invalid input.")
                continue
            break
