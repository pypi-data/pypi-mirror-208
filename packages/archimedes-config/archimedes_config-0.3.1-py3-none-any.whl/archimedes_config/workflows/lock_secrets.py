"""
Workflow for locking config
"""

from archimedes_config.workflows.workflow_base import WorkflowBase


class LockConfig(WorkflowBase):
    """workflow for locking secret"""

    def set_encrypted_key(self, encryption_key=None):
        """Sets encryption key"""
        if self.config_has_remote_conn_parameters():
            if encryption_key:
                raise Exception(
                    "Config set to connect to azure keyvault. `encryption_key` should not be set."
                )
            self.conf.set_default_key_from_key_vault()
        else:
            self.conf.set_default_key(encryption_key)

        if not self.conf.is_config_encrypted:
            self.conf.encrypt_configs()

    def _loop_for_secret(self):
        """
        Bypass parent class prompts to add secrets
        """

    def save(self, file_name, save_decrypted=False):
        """Saves the config"""
        super().save(file_name, save_decrypted=save_decrypted)
