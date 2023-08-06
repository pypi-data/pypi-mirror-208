"""Module to download file with a progressbar."""

import logging
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import internetarchivesync.observer

log = logging.getLogger(__name__)


def downloaded_size(file_path: str) -> int:
    """Returns the size of the file or zero if file is missing.

    Args:
        file_path (str): file path.

    Returns:
        int: size of the file or if file is missing.
    """

    return os.stat(file_path).st_size if os.path.isfile(file_path) else 0


def download(
    observer: internetarchivesync.observer.ProgressObserver,
    base_dir: str,
    url: str,
    auth: requests.auth.AuthBase,
    resume: bool = False,
) -> str:
    """Download file.

    Args:
        observer (Observer): Observer.
        base_dir (str): destination directory.
        url (str): url of the desired file.
        auth (requests.auth.AuthBase): requests.auth.AuthBase to use for download.
        resume (bool, optional): Try to resume download or not. Defaults to False.

    Returns:
        str: path of the downloaded file.
    """

    # Inspired by https://gist.github.com/tobiasraabe/58adee67de619ce621464c1a6511d7d9

    timeout = 500
    filename = url.split("/")[-1]
    file = os.path.join(base_dir, filename)

    resume_byte_pos = None
    if resume:
        resume_byte_pos = downloaded_size(file)

    # Go to the final url first
    # https://github.com/psf/requests/issues/2949
    response = requests.head(url, auth=auth, allow_redirects=True, timeout=timeout)
    final_url = response.url

    response = requests.head(
        final_url, auth=auth, allow_redirects=True, timeout=timeout
    )
    file_size = int(response.headers.get("content-length", 0))
    if file_size == 0:
        if response.status_code == 200 and resume:
            log.info("Restart download.")
            return download(observer, base_dir, url, auth, False)

    observer.started(file_size, f"Downloading '{filename}'")

    # Append information to resume download at specific byte position
    # to header
    resume_header = {"Range": f"bytes={resume_byte_pos}-"} if resume_byte_pos else None

    # Establish connection
    session = requests.Session()
    retries = Retry(total=10, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        with session.get(
            final_url, stream=True, headers=resume_header, auth=auth
        ) as response:
            response.raise_for_status()
            # Set configuration
            block_size = 1024
            initial_pos = resume_byte_pos if resume_byte_pos else 0
            observer.update(initial_pos)
            mode = "ab" if resume_byte_pos else "wb"
            with open(file, mode) as filep:
                for chunk in response.iter_content(32 * block_size):
                    filep.write(chunk)
                    observer.update(len(chunk))
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 416:
            # 416: Requested Range Not Satisfiable
            # We try to resume the download in the wrong place so it is better to start
            # from scratch.
            log.warning(
                f"Unable to resume download for '{url}' (redirect to '{final_url}')"
                "(status code 416)."
            )
            log.info("Restart download.")
            return download(observer, base_dir, url, auth, False)
        else:
            log.error(
                f"Error during donwload for '{url}' (redirect to '{final_url}')"
                f"(status code {error.response.status_code})."
            )
            raise

    resume_byte_pos = downloaded_size(file)
    if file_size != 0 and file_size != resume_byte_pos:
        log.info(
            f"File downloaded for '{url}' is incomplete "
            f"({resume_byte_pos}/{file_size})."
        )
        log.info("Resume download.")
        return download(observer, base_dir, url, auth, True)

    observer.completed()
    return file
