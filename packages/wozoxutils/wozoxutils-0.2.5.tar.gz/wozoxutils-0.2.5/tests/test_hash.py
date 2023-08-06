import unittest

from wozoxutils import calculate_md5_for_file, calculate_md5_for_files


class TestHash(unittest.TestCase):
    def test_hash(self):
        md5_hash = calculate_md5_for_file('tests/foo.json')
        self.assertEqual(md5_hash, 'eb7a203770342c5d4336d41cf1d7c05b')
        md5_hash = calculate_md5_for_files(['tests/foo.yaml', 'tests/foo.json'])
        self.assertEqual(md5_hash, '1e073343d8616c486391901bdd41a7af')

if __name__ == '__main__':
    unittest.main()