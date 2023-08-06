"""Module to download archive from archive.org."""

import logging
import os
from typing import Optional, Tuple

import requests

import internetarchivesync.download

log = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Authentication Failed."""


class S3Auth(requests.auth.AuthBase):
    """Attaches S3 Basic Authentication to the given Request object."""

    def __init__(self, access_key: str, secret_key: str):
        self.access_key: str = access_key
        self.secret_key: str = secret_key

    def __call__(
        self, prepared_request: requests.models.PreparedRequest
    ) -> requests.models.PreparedRequest:
        if not self.access_key:
            if self.secret_key:
                raise AuthenticationError("No access_key set!")
        if not self.secret_key:
            if self.access_key:
                raise AuthenticationError("No secret_key set!")
            else:
                raise AuthenticationError("No access_key or secret_key set!")

        prepared_request.headers[
            "Authorization"
        ] = f"LOW {self.access_key}:{self.secret_key}"

        return prepared_request


def get_access_secret_s3_tuple(host: str, email: str, password: str) -> Tuple[str, str]:
    """Returns the tuple (access, secret) required for S3 Basic Authentication.

    Args:
        host (str): archive.org host.
        email (str): email of archive.org account.
        password (str): password of archive.org account.

    Returns:
        Tuple[str, str]: (access, secret) tuple required for S3 Basic Authentication.
    """

    url = f"https://{host}/services/xauthn/"
    params = dict(op="login")
    data = dict(email=email, password=password)
    response = requests.post(url, params=params, data=data, timeout=500)
    json_response = response.json()

    access = json_response["values"]["s3"]["access"]
    secret = json_response["values"]["s3"]["secret"]

    return (access, secret)


def create_tree_structure(base_dir: str, identifier: str, file_path: str) -> str:
    """Create the tree structure to download an archive.org file.

    Args:
        base_dir (str): root directory which contains archive.org archives.
        identifier (str): identifier of archive.org archive.
        file_path (str): desired archive file.

    Returns:
        str: path of the created directory.
    """

    base_dir = os.path.join(base_dir, identifier)
    dir_path = os.path.join(base_dir, os.path.dirname(file_path))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def download_archive_files(
    observer: internetarchivesync.observer.ProgressObserver,
    email: str,
    password: str,
    base_dir: str,
    identifier: str,
    file_path: str,
) -> str:
    """Download an archive.org file.

    Args:
        email (str): email of archive.org account.
        password (str): email of archive.org account.
        base_dir (str): root directory which contains archive.org archives.
        identifier (str): identifier of archive.org archive.
        file_path (str): desired archive file.

    Returns:
        str: path of the download file.
    """

    host = "archive.org"
    (access, secret) = get_access_secret_s3_tuple(host, email, password)
    auth = S3Auth(access, secret)

    url = f"https://{host}/download/{identifier}/{file_path}"
    dir_path = create_tree_structure(base_dir, identifier, file_path)

    return internetarchivesync.download.download(observer, dir_path, url, auth, True)


if __name__ == "__main__":
    pass
