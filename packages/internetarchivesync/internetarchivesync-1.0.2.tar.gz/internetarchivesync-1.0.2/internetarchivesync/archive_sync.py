"""Module to synchronize a local archive with the one on archive.org."""

import functools
import logging
import os
from typing import Any, Callable, Iterable, List, Optional, Set, Tuple

import defusedxml.ElementTree as ET

import internetarchivesync.io
import internetarchivesync.observer

log = logging.getLogger(__name__)


class ArchiveSync:
    """Class to synchronize a local archive with the one on archive.org."""

    def __init__(self, base_dir: str, archive_name: str):
        self.base_dir: str = base_dir
        self.archive_name: str = archive_name
        self.metadatas: Set[str] = set()

    @functools.cached_property
    def reference_file(self) -> str:
        """Returns the file path of the reference file.

        Args:
            archive_name (str): archive name / identifier.

        Returns:
            [type]: the file path of the referenec file.
        """
        return f"{self.archive_name}_files.xml"

    @functools.cached_property
    def local_archive_content(self) -> dict[str, Optional[Tuple[int, str]]]:
        """Returns the content of the local archive.

        Returns:
            dict[str, Optional[Tuple[int, str]]]: Content of the local archive.
        """

        dst = {}  # type: dict[str, Optional[Tuple[int, str]]]
        dirname = os.path.join(self.base_dir, self.archive_name)
        for dirpath, _, filenames in os.walk(dirname):
            for file in filenames:
                fullpath = os.path.join(dirpath, file)
                rel = os.path.relpath(fullpath, start=dirname).replace("\\", "/")
                dst[rel] = None

        return dst

    @functools.cached_property
    def remote_archive_content(
        self,
    ) -> dict[str, tuple[int, str]]:
        """Returns the content of the archive.org described in reference file.

        Args:
            content_directory (str): Directory which contains the archive.
            archive_name (str): Name of the archive.

        Returns:
            dict[str, tuple[int, str]]: Hash table of files where the key is the
            filename and the value is a tupe of size and MD5 checksum.
        """

        xmlfilename = self.reference_file
        xmlfile = os.path.join(
            self.base_dir, os.path.join(self.archive_name, xmlfilename)
        )

        root = ET.parse(xmlfile).getroot()
        src = {}
        for file_elt in root.findall("file"):
            filename = file_elt.get("name")
            if filename is not None:
                md5_elt = file_elt.find("md5")
                size_elt = file_elt.find("size")
                format_elt = file_elt.find("format")
                if format_elt is not None and format_elt.text == "Metadata":
                    self.metadatas.add(filename)
                if md5_elt is not None:
                    if size_elt is not None and size_elt.text is not None:
                        try:
                            size_of_src = int(size_elt.text)
                        except ValueError:
                            size_of_src = 0
                        md5_of_src = md5_elt.text
                        if md5_of_src:
                            src[filename] = (size_of_src, md5_of_src)
                    else:
                        log.warning(f"Missing size {filename}")
                        src[filename] = (0, md5_elt.text)  # _files.xml has no size
                else:
                    log.warning(f"Missing md5 {filename}")
            else:
                log.warning(f"Missing file {filename}")

        return src

    def move_file_to_cave(
        self,
        observer: internetarchivesync.observer.ProgressObserver,
        file_path: str,
    ) -> None:
        """Move file to cave.

        Args:
            observer (Observer): Observer.
            file_path (str): desired archive file.
        """

        cave_archive_base_dir = os.path.join(self.base_dir, f"cave_{self.archive_name}")
        archive_base_dir = os.path.join(self.base_dir, self.archive_name)
        source_file_path = os.path.join(archive_base_dir, file_path)
        destination_file_path = os.path.join(cave_archive_base_dir, file_path)
        destination_dir = os.path.dirname(destination_file_path)

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        os.rename(source_file_path, destination_file_path)

    def move_to_cave(self) -> None:
        """Move files to cave."""

        only_localy = (
            set(self.local_archive_content.keys())
            - set(self.remote_archive_content.keys())
            - set(self.metadatas)  # Don't move metadatas
        )
        move_job = []  # type: List[Tuple[Callable[..., Any], Tuple[Any, ...]]]
        for file_to_move in only_localy:
            move_job.append((self.move_file_to_cave, (file_to_move,)))
        _ = internetarchivesync.observer.manage_jobs(
            move_job, "Moving files to *cave*".ljust(32), 1
        )

    def compare(
        self,
        skip_md5: bool,
        recheck: Optional[Iterable[str]] = None,
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Check locals files.

        Args:
            skip_md5 (bool): Use file size only.
            recheck (Iterable[str]): Re-check this locals files only. Defaults to None.

        Returns:
            Tuple[Iterable[str], Iterable[str], Iterable[str], Iterable[str]]: Tuples
            with the result of comparaison:
                * only_localy: files present only localy
                * bad: files with different size or bad md5
                * good: files with bad size or bad md5
                * only_remotely: files present on both side
        """

        # files present only localy
        only_localy = set(self.local_archive_content.keys()) - set(
            self.remote_archive_content.keys()
        )
        # files present only remotely
        only_remotely = set(self.remote_archive_content.keys()) - set(
            self.local_archive_content.keys()
        )
        # files present on both side
        on_both_side = set(self.remote_archive_content.keys()) & set(
            self.local_archive_content.keys()
        )

        bad = []
        good = []

        if recheck is None:
            files_to_check = on_both_side  # type: Iterable[str]
        else:
            files_to_check = recheck

        hash_job = []  # type:List[Tuple[Callable[..., Any], Tuple[Any, ...]]]
        for file_to_check in files_to_check:
            file_path = os.path.join(self.base_dir, self.archive_name, file_to_check)
            hash_job.append(
                (internetarchivesync.io.get_file_info, (file_path, skip_md5))
            )

        if not skip_md5:
            msg = "File comparisons using md5 hash "
        else:
            msg = "File comparisons using file size"
        results = internetarchivesync.observer.manage_jobs(hash_job, msg)
        hash_results = {file_path: result for (file_path, *result) in results}

        for file_to_check in files_to_check:
            file_path = os.path.join(self.base_dir, self.archive_name, file_to_check)
            (dst_file_size, dst_file_hash_md5) = hash_results[file_path]
            self.local_archive_content[file_to_check] = (
                dst_file_size,
                dst_file_hash_md5,
            )
            (src_file_size, src_file_hash_md5) = self.remote_archive_content[
                file_to_check
            ]
            if skip_md5:
                if src_file_size == dst_file_size:
                    good.append(file_to_check)
                else:
                    bad.append(file_to_check)
            else:
                if src_file_hash_md5 == dst_file_hash_md5:
                    good.append(file_to_check)
                else:
                    bad.append(file_to_check)

        # We assume that reference file is always good
        if self.reference_file in bad:
            bad.remove(self.reference_file)
        if self.reference_file not in good:
            good.append(self.reference_file)

        return (list(only_localy), good, bad, list(only_remotely))
