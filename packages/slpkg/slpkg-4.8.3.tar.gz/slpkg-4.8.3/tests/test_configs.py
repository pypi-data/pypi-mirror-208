import unittest
from slpkg.configs import Configs
from pathlib import Path


class TestConfigs(unittest.TestCase):

    def setUp(self):
        self.configs = Configs

    def test_configs(self):
        self.assertEqual('slpkg', self.configs.prog_name)
        self.assertEqual('x86_64', self.configs.os_arch)
        self.assertEqual(Path('/tmp'), self.configs.tmp_path)
        self.assertEqual(Path('/tmp/slpkg'), self.configs.tmp_slpkg)
        self.assertEqual(Path('/tmp/slpkg/'), self.configs.download_only_path)
        self.assertEqual(Path('/var', 'lib', 'slpkg'), self.configs.lib_path)
        self.assertEqual(Path('/etc', 'slpkg'), self.configs.etc_path)
        self.assertEqual(Path('/var/lib/', 'slpkg', 'database'), self.configs.db_path)
        self.assertEqual(Path('/var', 'log', 'packages'), self.configs.log_packages)

        self.assertEqual('database.slpkg', self.configs.database_name)
        self.assertEqual('.pkgs', self.configs.file_list_suffix)
        self.assertEqual('upgradepkg --install-new', self.configs.installpkg)
        self.assertEqual('upgradepkg --reinstall', self.configs.reinstall)
        self.assertEqual('removepkg', self.configs.removepkg)
        self.assertEqual(True, self.configs.colors)
        self.assertEqual(True, self.configs.dialog)
        self.assertEqual('wget', self.configs.downloader)
        self.assertEqual('-c -q --progress=bar:force:noscroll --show-progress', self.configs.wget_options)
        self.assertEqual('', self.configs.curl_options)
        self.assertEqual('-c get -e', self.configs.lftp_get_options)
        self.assertEqual('-c mirror --parallel=100 --only-newer', self.configs.lftp_mirror_options)
        self.assertEqual(True, self.configs.silent_mode)
        self.assertEqual(True, self.configs.ascii_characters)
        self.assertEqual(True, self.configs.ask_question)
        self.assertEqual(False, self.configs.parallel_downloads)
        self.assertEqual('*', self.configs.file_pattern)
        self.assertEqual('pixel', self.configs.progress_spinner)
        self.assertEqual('green', self.configs.spinner_color)
        self.assertEqual('', self.configs.proxy_address)
        self.assertEqual('', self.configs.proxy_username)
        self.assertEqual('', self.configs.proxy_password)


if __name__ == '__main__':
    unittest.main()
