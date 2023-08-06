import io
import logging

from typing import Protocol
from dataclasses import dataclass

from azure.storage.blob import ContainerClient
from azure.identity import DefaultAzureCredential

from azurify.azsecrets import AzureSecrets
from azurify.azconverter import factory, Suffix


@dataclass
class ObjectToStore:
    """Object information including name, in which container it should reside
    and the data to be stored
    """

    object_name: str
    container_name: str
    data_to_store: io.BytesIO


class CloudStorageUploader(Protocol):
    """Protocol class for storing data in various cloud storages"""

    def __init__(self, storage_object: ObjectToStore, **credentials):
        ...

    def export(self) -> None:
        ...


class AzureBlobUploader:
    """Handler for storing data in Azure Blob Storage"""

    def __init__(self, object_to_store: ObjectToStore, conn_str: str):
        """_summary_

        Args:
            storage_object (ObjectToStore): contains filename, container/folder and data
            conn_str (str): Azure storage connection string
        """
        # unpack ObjectToStore
        self.container_name = object_to_store.container_name
        self.file_name = object_to_store.object_name
        self.data_to_store = object_to_store.data_to_store

        # Azure Storage Connection String
        self.conn_str = conn_str

    def _container(self) -> ContainerClient:
        """Getter for container. If container doesn't exist, it's created

        Returns:
            ContainerClient: Azure object for handling blob container operations
        """
        container = ContainerClient.from_connection_string(
            conn_str=self.conn_str, container_name=self.container_name
        )
        if not container.exists:
            container.create_container()
            logging.info(
                f"Created container `{self.container_name}` because it didn't exist."
            )

        return container

    def upload(self):
        """Upload the data to Azure blob"""
        container = self._container()
        blob_client = container.get_blob_client(self.file_name)
        blob_client.upload_blob(self.data_to_store, overwrite=True)
        logging.info(
            f"Created blob `{self.file_name}` in container `{self.container_name}`"
        )


def main():
    print(f"executing {__name__} in {__file__}")
    data = [{"createdAt": 2021, "price": 10}, {"createdAt": 2022, "price": 20}]
    suffix = Suffix.CSV
    converter = factory(suffix)
    converted_data = converter.convert(data).data

    object_to_store = ObjectToStore(
        object_name=f"data.{suffix}",
        container_name="testcontainer2",
        data_to_store=converted_data,
    )

    conn_str = AzureSecrets(
        vault_url="https://kv-langerchen.vault.azure.net/",
        credential=DefaultAzureCredential(),
    ).AZSTORAGECONNSTR

    AzureBlobUploader(object_to_store=object_to_store, conn_str=conn_str).upload()


if __name__ == "__main__":
    main()
