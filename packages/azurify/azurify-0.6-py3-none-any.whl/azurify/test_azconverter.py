import unittest

from azconverter import *


class TestConverter(unittest.TestCase):
    def setUp(self):
        pass

    def test_converter_factory(self):
        cf = factory(output_type=Suffix.JSON.value)
        self.assertIsInstance(cf, JSONConverter)
        cf = factory(output_type=Suffix.CSV.value)
        self.assertIsInstance(cf, CSVConverter)
        cf = factory(output_type=Suffix.XLSX.value)
        self.assertIsInstance(cf, ExcelConverter)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
