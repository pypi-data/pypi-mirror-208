""" Tool to donwload and update an archive.org's archive. """

import argparse
import importlib.resources
import logging
import logging.config
from typing import Any, Callable, List, Tuple

from rich.console import Console

import internetarchivesync.archive_download as archive_download
import internetarchivesync.archive_sync as archive_sync
import internetarchivesync.observer as observer

log = logging.getLogger(__name__)

logging.config.fileConfig(
    importlib.resources.open_text(__package__, "logging_config.ini")
)

parser = argparse.ArgumentParser(
    prog="async",
    description="Synchronise une archive local à partir de la version sur archive.org",
)
parser.add_argument("name", help="Nom de l'archive archive.org.", action="store")
parser.add_argument("-l", "--login", help="Login archive.org.", action="store")
parser.add_argument("-p", "--password", help="Password archive.org.", action="store")
parser.add_argument(
    "-b",
    "--dir",
    help="Répertoire contenant l'archive locale.",
    action="store",
    default=".",
)
parser.add_argument(
    "-c",
    "--check",
    help="Vérifie l'archive locale.",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-d", "--dry-run", help="Simule les actions.", action="store_true", default=False
)

parser.add_argument(
    "-s",
    "--skip-md5",
    help="Fait la uniquement via la taille des fichiers et non le hash MD5.",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-i",
    "--init",
    help="Crée l'aborescence de l'archive locale.",
    action="store_true",
    default=False,
)


parser.print_help()

args = parser.parse_args()
CONTENT_DIRECTORY = args.dir
ARCHIVE_NAME = args.name
DRY_RUN = args.dry_run
LOGIN = args.login
PASSWORD = args.password
check_only = args.check
SKIP_MD5 = args.skip_md5
INIT = args.init

console = Console()
sync = archive_sync.ArchiveSync(CONTENT_DIRECTORY, ARCHIVE_NAME)

# On crée l'arborescence pour stocker l'archive locale
if INIT:
    reference_file = sync.reference_file
    archive_download.download_archive_files(
        observer.ProgressObserver(0),
        LOGIN,
        PASSWORD,
        CONTENT_DIRECTORY,
        ARCHIVE_NAME,
        reference_file,
    )

# Move to files to *cave*
sync.move_to_cave()

# Compare
(only_localy, good, bad, only_remotely) = sync.compare(SKIP_MD5)

log.debug(f"only_localy={only_localy}")
log.debug(f"good={good}")
log.debug(f"bad={bad}")
log.debug(f"only_remotely={only_remotely}")

re_good = []  # type: List[str]
re_bad = []  # type: List[str]

if check_only:
    console.print(f":cake: File to keep ({len(good)}):")
    for f in good:
        console.print(f"  ✅ [green]{f}[/green]")
    console.print(f":sad_but_relieved_face: File to redownload ({len(bad)}):")
    for f in bad:
        console.print(f"  ❌ [red]{f}[/red]")
    console.print(f":sad_but_relieved_face: File to download ({len(only_remotely)}):")
    for f in only_remotely:
        console.print(f"  ❌ [red]{f}[/red]")
else:
    dl_job = []  # type:List[Tuple[Callable[..., Any], Tuple[Any, ...]]]
    to_redownload = set(only_remotely) | set(bad)

    for f in to_redownload:
        dl_job.append(
            (
                archive_download.download_archive_files,
                (LOGIN, PASSWORD, CONTENT_DIRECTORY, ARCHIVE_NAME, f),
            )
        )

    _ = observer.manage_jobs(dl_job, "Downloading missing files".ljust(32), 1)
    (_, re_good, re_bad, _) = sync.compare(SKIP_MD5, list(to_redownload))

log.debug(f"re_good={re_good}")
log.debug(f"re_bad={re_bad}")

good_set = set(good) | set(re_good)
remote_set = set(sync.remote_archive_content)

if good_set == remote_set:
    console.print("")
    console.print("Sync ! ✨ 🍰 ✨")
    exit(0)
else:
    console.print("")
    console.print("Not sync :-/")
    if (good_set | sync.metadatas) == remote_set:
        console.print(
            f"... but only some metadatas are not sync ! {remote_set - good_set}"
        )
    exit(1)
