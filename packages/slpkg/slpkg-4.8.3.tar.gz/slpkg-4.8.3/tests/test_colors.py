import unittest
from slpkg.configs import Configs


class TestColors(unittest.TestCase, Configs):

    def setUp(self):
        super(Configs, self).__init__()

    def test_colors(self):
        self.assertEqual('\033[32;5m', self.blink)
        self.assertEqual('\033[1m', self.bold)
        self.assertEqual('\x1b[91m', self.red)
        self.assertEqual('\033[1m\x1b[91m', self.bred)
        self.assertEqual('\x1b[32m', self.green)
        self.assertEqual('\033[1m\x1b[32m', self.bgreen)
        self.assertEqual('\x1b[93m', self.yellow)
        self.assertEqual('\033[1m\x1b[93m', self.byellow)
        self.assertEqual('\x1b[96m', self.cyan)
        self.assertEqual('\x1b[94m', self.blue)
        self.assertEqual('\x1b[38;5;247m', self.grey)
        self.assertEqual('\x1b[35m', self.violet)
        self.assertEqual('\x1b[0m', self.endc)


if __name__ == '__main__':
    unittest.main()
