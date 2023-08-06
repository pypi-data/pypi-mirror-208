import json
import logging

from typing import Protocol
from strenum import StrEnum
from enum import auto

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class AzSecretKeys(StrEnum):
    SHOPDOMAIN = auto()
    APIVERSION = auto()
    APIACCESSTOKEN = auto()
    APICLIENTSECRETKEY = auto()
    AZSTORAGECONNSTR = auto()


class Secrets(Protocol):
    def __init__(self, **tresor_params):
        ...

    def load_json(self, path: str) -> None:
        ...

    @property
    def secrets(self):
        ...

    def set_secret(key: str, value: str) -> None:
        ...

    def get_secret(self, key):
        ...


class AzureSecrets:
    def __init__(self, vault_url: str, credential):
        """Populate secrets dict with Keys/Values from the Azure KeyVault and create
        an instance attribute for each secret

        Args:
            vault_url (str): _description_
            credential (_type_): _description_
        """
        self._secrets = dict()
        self._secret_client = SecretClient(vault_url=vault_url, credential=credential)

        for secret in self._secret_client.list_properties_of_secrets():
            key = secret.name
            value = self._secret_client.get_secret(secret.name).value
            # create entry in secrets dict
            self._secrets[key] = value
            # create instance attribute
            setattr(self, key, value)

    def load_jsonfile(self, path: str) -> None:
        """Load secrets from file

        Args:
            path (str): JSON path
        """
        with open(path) as json_data:
            config_secrets = json.load(json_data)

        # populate
        for enum in AzSecretKeys:
            if enum.name in [k for k in config_secrets.keys()]:
                # create secrets in Azure keyvault
                self.set_secret(enum.name, config_secrets[enum.name])
                # create instance attribute
                setattr(self, enum.name, config_secrets[enum.name])
            else:
                # file contains keys which are not allowed
                logging.warning(
                    f"Key `{enum.name}` contained in `SecretKey(StrEnum)`but not in `{path}` data: {config_secrets.keys()} "
                )

    @property
    def secrets(self) -> dict:
        """All secrets in dict

        Returns:
            dict: secret key and value
        """
        return self._secrets

    def set_secret(self, key: str, value: str) -> None:
        """Create individual secret

        Args:
            key (str): Secret key
            value (str): Secret value
        """
        self._secrets[key] = value
        setattr(self, key, value)
        self._secret_client.set_secret(key, value)

    def get_secret(self, key: str) -> str:
        """Getter for secret

        Args:
            key (str): Secret key

        Returns:
            _type_: Secret value
        """
        return self._secret_client.get_secret(key)

    def delete_secret(self, key):
        poller = self.keyvault_client.begin_delete_secret(key)
        poller.result()


def main():
    print(f"executing {__name__} in {__file__}")
    """Simple test case"""
    secrets = AzureSecrets(
        vault_url="https://kv-langerchen.vault.azure.net/",
        credential=DefaultAzureCredential(),
    )

    print(secrets.SHOPDOMAIN)


if __name__ == "__main__":
    main()

    """
    secrets = AzureSecrets(vault_url="https://kv-langerchen.vault.azure.net/", credential=DefaultAzureCredential(),)
    """
