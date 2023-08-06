import json
from .file import ensure_dir_exists

def load_json(file_name: str):
    """
    Load json file

    :param file_name: File path
    :return: Content
    """
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_name: str, content, indent: int | str | None = None, sort_keys: bool = False):
    """
    Save json file. If the directory does not exist, it will be created.

    :param file_name: File path
    :param content: Content to save
    """
    ensure_dir_exists(file_name)
    with open(file_name, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(content, f, ensure_ascii=False, indent=indent, sort_keys=sort_keys)