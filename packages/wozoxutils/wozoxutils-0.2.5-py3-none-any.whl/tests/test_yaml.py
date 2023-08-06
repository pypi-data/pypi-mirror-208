import unittest

from wozoxutils import load_yaml, save_yaml


class TestYaml(unittest.TestCase):
    def test_yaml(self):
        yaml_obj = {
            'foo': 'bar',
            'int': 1
        }
        save_yaml('tests/foo.yaml', yaml_obj)

        yaml_obj = load_yaml('tests/foo.yaml')
        self.assertEqual(yaml_obj['foo'], 'bar')
        self.assertEqual(yaml_obj['int'], 1)

if __name__ == '__main__':
    unittest.main()