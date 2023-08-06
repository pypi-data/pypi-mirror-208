# Testing creation an deletion of an azure keyvault

import unittest
import random
import string

from azkeyvault import Keyvault, keyvault_client


class TestAzureKeyvault(unittest.TestCase):
    """Test creation an deletion of an azure keyvault

    Args:
        unittest (_type_): _description_
    """

    def setUp(self):
        # create a random name for the keyvault
        random_str = "".join(random.choices(string.ascii_lowercase, k=10))
        self.tresor_name = f"test-kv-{random_str}"
        # create keyvault_client and keyvault objects
        self.kv_client = keyvault_client()
        self.kv = Keyvault(tresor_name=self.tresor_name, keyvault_client=self.kv_client)

    def test_keyvault_create(self):
        # create keyvault and check if it's lists in the azure keyvaults
        self.kv.create()
        kv_list = [kv.name for kv in self.kv_client.vaults.list()]
        self.assertIn(self.tresor_name, kv_list)

    def test_keyvault_delete(self):
        # delete previously created keyvault and check if it's missing in the list of the azure keyvaults
        kv = Keyvault(tresor_name=self.tresor_name, keyvault_client=self.kv_client)
        kv.delete()
        kv_list = [kv.name for kv in self.kv_client.vaults.list()]
        self.assertNotIn(self.tresor_name, kv_list)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
