import random
import string
import unittest
import json
import os

from azure.identity import DefaultAzureCredential

from azkeyvault import Keyvault, keyvault_client
from azsecrets import AzureSecrets


class TestAzureSecrets(unittest.TestCase):
    def setUp(self):
        # Create randomized keyvault name and keyvault
        _random_str = "".join(random.choices(string.ascii_lowercase, k=10))
        _keyvault_name = f"kv-test-{_random_str}"
        Keyvault(tresor_name=_keyvault_name, keyvault_client=keyvault_client()).create()

        # create secrets management object
        self.azsecrets = AzureSecrets(
            vault_url=f"https://{_keyvault_name}.vault.azure.net/",
            credential=DefaultAzureCredential(),
        )

        # test data
        self.test_data = {
            "SHOPDOMAIN": "dcboard.myshopify.com",
            "APIVERSION": "2023-04",
            "APIACCESSTOKEN": "111",
            "APICLIENTSECRETKEY": "222",
            "AZSTORAGECONNSTR": "abc",
        }
        self.azsecrets.load_json("test_data.json")

        # test-data with invalid keys
        self.test_data_incorrect_keys = {
            "SHOP_DOMAIN": "dcboard.myshopify.com",
            "API_VERSION": "2023-04",
            "APIACCESSTOKEN": "111",
            "APICLIENTSECRETKEY": "222",
            "AZSTORAGECONNSTR": "abc",
        }

        json_object = json.dumps(self.test_data, indent=4)
        json_object_incorrect = json.dumps(self.test_data_incorrect_keys, indent=4)

        # create json files
        with open("test_data.json", "w") as outfile:
            outfile.write(json_object)

        with open("test_data_incorrect_keys.json", "w") as outfile:
            outfile.write(json_object_incorrect)

    def test_load_jsonfile(self):
        # read secrets data from file
        secrets = AzureSecrets(
            vault_url=f"https://{self._keyvault_name}.vault.azure.net/",
            credential=DefaultAzureCredential(),
        )
        secrets.load_json("test_data.json")
        assert secrets.SHOPDOMAIN == "dcboard.myshopify.com"

    def test_load_file_with_wrong_keys(self):
        secrets = AzureSecrets(
            vault_url=f"https://{self._keyvault_name}.vault.azure.net/",
            credential=DefaultAzureCredential(),
        )
        secrets.load_json("test_data_incorrect_keys.json")

        with self.assertRaises(AttributeError):
            assert secrets.SHOP_DOMAIN == "dcboard.myshopify.com"

    def test_secrets(self):
        # test property access
        assert self.azsecrets.SHOPDOMAIN == "dcboard.myshopify.com"
        assert self.azsecrets.APIVERSION == "2023-04"
        assert self.azsecrets.APIACCESSTOKEN == "111"
        assert self.azsecrets.APICLIENTSECRETKEY == "222"
        assert self.azsecrets.AZSTORAGECONNSTR == "abc"

        # test dict access
        assert self.azsecrets.secrets["SHOPDOMAIN"] == "dcboard.myshopify.com"
        assert self.azsecrets.secrets["APIVERSION"] == "2023-04"
        assert self.azsecrets.secrets["APIACCESSTOKEN"] == "111"
        assert self.azsecrets.secrets["APICLIENTSECRETKEY"] == "222"
        assert self.azsecrets.secrets["AZSTORAGECONNSTR"] == "abc"

    def test_set_secret(self):
        self.azsecrets.set_secret("NEWKEY", "def")
        assert self.azsecrets.NEWKEY == "def"
        assert self.azsecrets.secrets["NEWKEY"] == "def"

    def test_get_secret(self):
        self.azsecrets.set_secret("NEWKEY", "def")
        assert self.azsecrets.NEWKEY == "def"
        assert self.azsecrets.secrets["NEWKEY"] == "def"

    def tearDown(self):
        os.system("rm test_data*.json")


if __name__ == "__main__":
    unittest.main()
