import unittest

from wozoxutils import load_json, save_json


class TestJson(unittest.TestCase):
    def test_json(self):
        json_obj = {
            'foo': 'bar',
            'int': 1
        }
        save_json('tests/foo.json', json_obj)

        json_obj = load_json('tests/foo.json')
        self.assertEqual(json_obj['foo'], 'bar')
        self.assertEqual(json_obj['int'], 1)

if __name__ == '__main__':
    unittest.main()