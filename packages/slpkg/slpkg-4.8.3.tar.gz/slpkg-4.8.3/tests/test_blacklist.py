import unittest
from slpkg.blacklist import Blacklist


class TestBlacklist(unittest.TestCase):

    def test_blacklist(self):
        black = Blacklist()
        self.assertListEqual([], black.packages())


if __name__ == '__main__':
    unittest.main()
