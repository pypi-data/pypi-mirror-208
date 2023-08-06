import unittest
from slpkg.checks import Check
from slpkg.sbos.queries import SBoQueries


class TestPkgInstalled(unittest.TestCase):

    def setUp(self):
        self.bin_queries = SBoQueries('sbo')
        self.data = self.bin_queries.repository_data()
        self.check = Check('sbo', self.data)
        self.packages = ['audacity', 'Flask', 'awscli']

    def test_check_exists(self):
        self.assertIsNone(self.check.package_exists_in_the_database(self.packages))

    def test_check_unsupported(self):
        self.assertIsNone(self.check.is_package_unsupported(self.packages))

    def test_check_is_installed(self):
        self.assertIsNone(self.check.is_package_installed(self.packages))


if __name__ == "__main__":
    unittest.main()
