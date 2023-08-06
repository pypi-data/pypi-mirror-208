import os
import sys
import random
import re
import string

from typing import Protocol
from dataclasses import dataclass

from azure.identity import DefaultAzureCredential
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.resource import ResourceManagementClient

from azurify.azsecrets import AzSecretKeys


DEFAULT_GROUP_NAME = os.environ.get("AZURE_DEFAULT_GROUP_NAME", None)
DEFAULT_LOCATION = os.environ.get("AZURE_DEFAULT_LOCATION", None)
DEFAULT_OBJECT_ID = os.environ.get("AZURE_DEFAULT_OBJECT_ID", None)
DEFAULT_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
DEFAULT_TENANT_ID = os.environ.get("AZURE_TENANT_ID", None)


@dataclass
class Secrets:
    secrets: dict()


@dataclass
class Secret:
    key: AzSecretKeys
    value: str


def resource_client(
    group_name: str = DEFAULT_GROUP_NAME, location: str = DEFAULT_LOCATION
) -> ResourceManagementClient:
    resource_client = ResourceManagementClient(
        credential = DefaultAzureCredential(),
        subscription_id = DEFAULT_SUBSCRIPTION_ID,
    )
    resource_client.resource_groups.create_or_update(group_name, {"location": location})
    return resource_client


def keyvault_client() -> KeyVaultManagementClient:
    return KeyVaultManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=DEFAULT_SUBSCRIPTION_ID,
    )

def generate_shopify_keyvault_name(shop_url: str) -> str:
    """Generate randomized name for keyvault of length 24

    Args:
        kv_name (str): desired name

    Returns:
        str: name with structure `kv-<name>-<random string>`eg. kv-aaaabbbb-bdgmbzynpbax 
    """

    kv_name = shop_url.split(".")[0]
    if re.match(kv_name, "^[\w-_]+$") == False:
        raise ValueError(f"Can not create an Azure keyvault from the shop_url `{shop_url}`. Only alphanumeric and hyphens are allowed")
    
    kv_name_length = len(kv_name)
    if kv_name_length > 20:
        return f"kv-{kv_name[:21]}"
    else:
        random_str_length = 20 - kv_name_length
        random_str = "".join(random.choices(string.ascii_lowercase, k=random_str_length))
        return f"kv-{kv_name[:kv_name_length]}-{random_str}"


class Tresor(Protocol):
    def create() -> None:
        ...

    def delete() -> None:
        ...


class Keyvault:
    def __init__(self, kv_name, keyvault_client=keyvault_client()):
        self.kv_name = kv_name
        self.keyvault_client = keyvault_client

    def create(self) -> None:
        self.keyvault_client.vaults.begin_create_or_update(
            DEFAULT_GROUP_NAME,
            self.kv_name,
            {
                "location": DEFAULT_LOCATION,
                "properties": {
                    "tenant_id": DEFAULT_TENANT_ID,
                    "sku": {"family": "A", "name": "standard"},
                    "access_policies": [
                        {
                            "tenant_id": DEFAULT_TENANT_ID,
                            "object_id": DEFAULT_OBJECT_ID,
                            "permissions": {
                                "secrets": [
                                    "get",
                                    "list",
                                    "set",
                                    "delete",
                                    "purge",
                                ],
                            },
                        }
                    ],
                    "enabled_for_deployment": True,
                    "enabled_for_disk_encryption": True,
                    "enabled_for_template_deployment": True,
                },
            },
        ).result()

    @property
    def keyvault(self):
        return self.keyvault_client.vaults.get(DEFAULT_GROUP_NAME, self.kv_name)

    def delete(self) -> None:
        self.keyvault_client.vaults.delete(DEFAULT_GROUP_NAME, self.kv_name)


def main(shop_url: str) -> None:
    """Create a keyvault out of a Shopify URL

    Args:
        shop_url (str): e.g. myshop.myshopify.com
    """
    kv_name = generate_shopify_keyvault_name(shop_url)
    kv = Keyvault(kv_name=kv_name)
    kv.create()

    print(f"Created keyvault `https://{kv.keyvault.name}.vault.azure.net`in `{kv.keyvault.location}`.")

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2 and args[0] in ["-kv", "--kv", "-kvname", "--kvname", "-keyvault-name", "--keyvault-name"]:
        main(args[1])
    else:
        print("Keyvault not created! Usage: `python create_keyvault.py -kvname test`")