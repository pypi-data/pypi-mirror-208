
import os


def ensure_dir_exists(path: str):
    """
    Ensure that the directory of the given path exists.

    :param path: Path to a file or directory.
    """
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    if not os.path.exists(path):
        os.makedirs(path)


def save_text(filename: str, content: str):
    """
    Save text to file. If the directory does not exist, it will be created.

    :param filename: File path
    :param content: Content to save
    """
    ensure_dir_exists(filename)
    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def load_text(filename: str) -> str:
    """
    Load text from file

    :param filename: File path
    :return: Content
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def save_bytes(filename: str, content: bytes):
    """
    Save bytes to file. If the directory does not exist, it will be created.

    :param filename: File path
    :param content: Content to save
    """
    ensure_dir_exists(filename)
    with open(filename, 'wb') as f:
        f.write(content)


def load_bytes(filename: str) -> bytes:
    """
    Load bytes from file

    :param filename: File path
    :return: Content
    """
    with open(filename, 'rb') as f:
        return f.read()
