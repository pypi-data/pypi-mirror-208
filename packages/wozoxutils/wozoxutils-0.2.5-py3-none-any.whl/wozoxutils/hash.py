
import hashlib


def calculate_md5_for_file(file_path: str) -> str:
    """
    Calculate the MD5 hash of the contents of a file.

    :param file_path: File path.
    :return: MD5 hash of the file contents.
    """
    md5_hash = hashlib.md5()

    with open(file_path, 'rb') as f:
        while chunk := f.read(1024*1024):  # 1MB
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def calculate_md5_for_files(file_list: list[str]) -> str:
    """
    Calculate the MD5 hash of the contents of all files in the given file list.

    :param file_list: List of file paths.
    :return: MD5 hash of the concatenated file contents.
    """
    md5_hash = hashlib.md5()

    for file_path in file_list:
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024*1024):  # 1MB
                md5_hash.update(chunk)

    return md5_hash.hexdigest()
