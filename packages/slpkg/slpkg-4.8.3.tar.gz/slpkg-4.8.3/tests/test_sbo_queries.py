import unittest
from slpkg.sbos.queries import SBoQueries


class TestSBoQueries(unittest.TestCase):

    def setUp(self):
        self.sbo_queries = SBoQueries('sbo')
        self.data: dict = self.sbo_queries.repository_data()
        self.name: str = 'slpkg'

    def test_slackbuild(self):
        self.assertTrue(True, self.data[self.name])

    def test_location(self):
        self.assertEqual('system', self.data[self.name]['location'])

    def test_sources_x86(self):
        self.assertEqual(['https://gitlab.com/dslackw/slpkg/-/archive'
                         '/4.8.2/slpkg-4.8.2.tar.gz'], self.data[self.name]['download'].split())

    def test_sources_x86_64(self):
        self.assertEqual([], self.data[self.name]['download64'].split())

    def test_requires(self):
        self.assertEqual(['SQLAlchemy', 'python3-pythondialog', 'python3-progress'],
                         self.data[self.name]['requires'].split())

    def test_version(self):
        self.assertEqual('4.8.2', self.data[self.name]['version'])

    def test_checksum_x86(self):
        self.assertListEqual(['96197dd92a2cc70e163eacdf83909252'], self.data[self.name]['md5sum'].split())

    def test_checksum_x86_64(self):
        self.assertListEqual([], self.data[self.name]['md5sum64'].split())

    def test_files(self):
        self.assertEqual(5, len(self.data[self.name]['files'].split()))

    def test_description(self):
        self.assertEqual('slpkg (Slackware Packaging Tool)', self.data[self.name]['description'])


if __name__ == '__main__':
    unittest.main()
