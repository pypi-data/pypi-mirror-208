""""Module to manage the progress of several tasks via the observer pattern."""

import logging
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from time import sleep
from typing import Any, Callable, List, Optional, Tuple

from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    DownloadColumn,
    FileSizeColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TotalFileSizeColumn,
    TransferSpeedColumn,
)

log = logging.getLogger(__name__)

DEBUG = False


class ProgressObserver:
    """ProgressObserver implements a sort of observer pattern to manage the progess of
    multiple tasks."""

    def __init__(self, task_id: int):
        """ProgressObserver constructor.

        Args:
            task_id (int): Task ID to manage.
        """

    def started(self, total: int, description: str = "") -> None:
        """Method to call when task start.

        Args:
            total (int): total number of steps.
            description (str): description of the task.
        """

    def update(self, advance: int) -> None:
        """Method to call when task progress.

        Args:
            advance (int): number of steps to advance.
        """

    def completed(self) -> None:
        """Method to call when task is completed."""

    def wraps_task(self, fun: Callable[..., Any], *args: Any) -> Any:
        """Wraps the task to force it to always be completed.

        Args:
            fun : Task to launch.
            args: Arguments to use.

        Returns:
            The result of fun call with arguments args.
        """
        try:
            if DEBUG:
                print(f"obs '{self}' fun '{self}' args '{args}'")
            return fun(self, *args)
        finally:
            if DEBUG:
                print(f"obs '{self}' COMPLETED")
            self.completed()


class RichProgressObserver(ProgressObserver):
    """RichProgressObserver implements ProgressObserver with RichProgress."""

    def __init__(self, rich_progress: Progress, task_id: int):
        """RichProgressObserver constructor.

        Args:
            rich_progress (Progress): Rich Progress object that manages the progression.
            task_id (int): Task ID to handle.
        """
        super().__init__(TaskID(task_id))
        self.rich_progress = rich_progress
        self.task_id: TaskID = TaskID(task_id)
        self.total: Optional[int] = None

    def started(self, total: Optional[int], description: str = "") -> None:
        if description:
            self.rich_progress.update(self.task_id, description=f"[cyan] {description}")
        self.rich_progress.tasks[self.task_id].visible = True
        self.rich_progress.update(self.task_id, total=total)
        self.total = total
        self.rich_progress.start_task(self.task_id)

    def update(self, advance: float) -> None:
        self.rich_progress.update(self.task_id, advance=advance)

    def completed(self) -> None:
        if self.total:
            self.rich_progress.update(self.task_id, completed=self.total)
        else:
            self.rich_progress.update(self.task_id, total=1)
            self.rich_progress.update(self.task_id, completed=1)
        self.rich_progress.tasks[self.task_id].visible = False


def manage_jobs(
    jobs: List[Tuple[Callable[..., Any], Tuple[Any, ...]]],
    description_of_jobs_group: str = "All Jobs",
    progression_type: int = 0,
) -> Any:
    """Manage the to-do list.

    Args:
        jobs (List[Tuple[Callable[..., Any], Tuple[Any, ...]]]): to-do list.
        overall_progress (Progress): Progress.
        description_of_jobs_group (str): Description of the to-do list group.

    Returns:
        The list of the returns of tasks.
    """

    if progression_type == 0:
        job_progress = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            FileSizeColumn(),
            TextColumn("/"),
            TotalFileSizeColumn()
            # TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
    else:
        job_progress = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn()
            # TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )

    total = len(jobs)
    overall_progress = Progress(
        "{task.description}", SpinnerColumn(), BarColumn(), MofNCompleteColumn()
    )
    overall_task = overall_progress.add_task(
        description_of_jobs_group, total=int(total)
    )

    progress_group = Group(
        job_progress,
        overall_progress,
    )

    futures = []

    with Live(progress_group, refresh_per_second=10):
        pool = ThreadPoolExecutor(max_workers=4)
        for fun, arg in jobs:
            task_id = job_progress.add_task("[cyan] truc", visible=False)
            rich_progress_observer = RichProgressObserver(job_progress, task_id)
            futures.append(pool.submit(rich_progress_observer.wraps_task, fun, *arg))
        while not overall_progress.finished:
            completed = 0
            for task in job_progress.tasks:
                if task.finished:
                    completed = completed + 1
            sleep(0.2)
            # print("NB COMPLETED", completed, "TOTAL ", total)
            overall_progress.update(overall_task, completed=completed)

    dones, _ = wait(futures, timeout=None, return_when=ALL_COMPLETED)
    results = []
    for done in dones:
        result = done.result()
        results.append(result)

    return results


if __name__ == "__main__":

    def task1(observer: ProgressObserver, param1: str, param2: str, param3: str) -> str:
        """Task of test."""
        observer.started(3)
        sleep(0.2)
        observer.update(1)
        sleep(0.2)
        observer.update(1)
        sleep(0.2)
        observer.update(1)
        observer.completed()
        return f"T1 {param1},{param2},{param3}"

    def task2(observer: ProgressObserver, array: List[str]) -> str:
        """Task of test."""
        observer.started(len(array))
        for _ in array:
            sleep(0.1)
            observer.update(1)
        observer.completed()
        return f"T2 {''.join(array)}"

    def task3(observer: ProgressObserver, array: List[str]) -> str:
        """Task of test."""
        observer.started(len(array))
        for _ in array:
            observer.update(1)
            raise Exception("test")
        observer.completed()
        return f"T3 {''.join(array)}"

    test_jobs = []  # type: List[ Tuple[Callable[..., Any], Tuple[Any, ...]] ]
    test_jobs.append(
        (
            task1,
            ("a", "b", "c"),
        )
    )
    test_jobs.append((task2, (["a", "b", "c"],)))
    test_jobs.append((task1, ("d", "e", "f")))
    test_jobs.append((task2, (["d", "e", "f"],)))
    test_jobs.append((task1, ("g", "h", "i")))
    test_jobs.append((task2, (["g", "h", "i"],)))
    test_jobs.append((task1, ("j", "k", "l")))
    test_jobs.append((task2, (["j", "k", "l"],)))
    test_jobs.append((task1, ("m", "n", "o")))
    # test_jobs.append((task3, (["a", "b", "c"],)))

    manage_jobs(test_jobs)
