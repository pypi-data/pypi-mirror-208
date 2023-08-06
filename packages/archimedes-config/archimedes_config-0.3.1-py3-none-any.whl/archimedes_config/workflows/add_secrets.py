"""
Workflow to add a secret to config
"""

from archimedes_config.workflows.workflow_base import WorkflowBase


class AddSecret(WorkflowBase):
    """Class for adding secret"""

    def set_encrypted_key(self, encryption_key=None):
        if self.config_has_remote_conn_parameters():
            if encryption_key:
                raise Exception(
                    "Config set to connect to azure keyvault. `encryption_key` should not be set."
                )
            self.conf.set_default_key_from_key_vault()
        else:
            self.conf.set_default_key(encryption_key)

        if self.conf.is_config_encrypted:
            self.conf.decrypt_configs()
