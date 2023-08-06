# wozoxutils [![PyPI](https://img.shields.io/pypi/v/wozoxutils.svg)](https://pypi.org/project/wozoxutils/) [![PyPI - Format](https://img.shields.io/pypi/format/wozoxutils.svg)](https://pypi.org/project/wozoxutils/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wozoxutils.svg)](https://pypi.org/project/wozoxutils/)
general-purpose library for Python that contains various commonly used functional modules.

## Installation

```shell
pip install wozoxutils
```

## Usage


```python
from wozoxutils import load_json, save_json, load_yaml, save_yaml, calculate_md5_for_file, calculate_md5_for_files

# json
json_obj = {
    'foo': 'bar',
    'int': 1
}
save_json('tests/foo.json', json_obj)
json_obj = load_json('tests/foo.json')
print(json_obj['foo']) # bar
print(json_obj['int']) # 1

# yaml
yaml_obj = {
    'foo': 'bar',
    'int': 1
}
save_yaml('tests/foo.yaml', yaml_obj)
yaml_obj = load_yaml('tests/foo.yaml')
print(yaml_obj['foo']) # bar
print(yaml_obj['int']) # 1

# md5
calculate_md5_for_file('tests/foo.json') # eb7a203770342c5d4336d41cf1d7c05b
calculate_md5_for_files(['tests/foo.yaml', 'tests/foo.json']) # 1e073343d8616c486391901bdd41a7af
```