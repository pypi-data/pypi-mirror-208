"""Module to calculate the MD5 checksum with a progress bar."""

import hashlib
import logging
import os
from typing import Optional, Tuple

import internetarchivesync.observer

log = logging.getLogger(__name__)


def md5_checksum(
    file_path: str, observer: internetarchivesync.observer.ProgressObserver
) -> str:
    """Calculate the MD5 checksum of the given file.

    Args:
        file_path (str): path of the file.

    Returns:
        str: MD5 checksum of the file.
    """

    block_size = 4096
    total_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    observer.started(total_size, f"hashing {filename}")
    with open(file_path, "rb") as file:
        hash_md5 = hashlib.new("md5", usedforsecurity=False)
        for chunk in iter(lambda: file.read(block_size * 32), b""):
            hash_md5.update(chunk)
            observer.update(len(chunk))
    observer.completed()
    return hash_md5.hexdigest()


def get_file_info(
    observer: internetarchivesync.observer.ProgressObserver,
    file_path: str,
    skip_md5: bool,
) -> Tuple[str, int, Optional[str]]:
    """Returns the tuple (file_size, file_hash_md5) of the given file.

    Args:
        file_path (str): path of the file.
        skip_md5 (bool): indicates we don't want MD5 checksum.

    Returns:
        Tuple[int, str]: (file_size, file_hash_md5) tuple with the size and the
        checksum of the file.
    """
    file_size = os.stat(file_path).st_size if os.path.isfile(file_path) else 0
    file_hash_md5 = None
    if not skip_md5:
        file_hash_md5 = md5_checksum(file_path, observer)

    return (file_path, file_size, file_hash_md5)
