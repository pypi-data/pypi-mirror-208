import yaml

from .file import ensure_dir_exists


def load_yaml(file_name: str):
    """
    Load yaml file

    :param file_name: File path
    :return: Content
    """
    with open(file_name, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def save_yaml(file_name: str, content, sort_keys: bool = False):
    """
    Save yaml file. If the directory does not exist, it will be created.

    :param file_name: File path
    :param content: Content to save
    """
    ensure_dir_exists(file_name)
    with open(file_name, 'w', encoding='utf-8', newline='\n') as f:
        yaml.dump(content, f, allow_unicode=True, sort_keys=sort_keys)