from multiprocessing import Queue
from typing import Callable, Iterable, TypeVar

from olympipe.pipes.task import TaskPipe

R = TypeVar("R")
S = TypeVar("S")


__version__ = "0.1.0"


class ExplodePipe(TaskPipe[R, S]):
    def __init__(
        self, source: "Queue[R]", task: Callable[[R], Iterable[S]], target: "Queue[S]"
    ):

        super().__init__(source, task, target)  # type: ignore

    def _send_to_next(self, processed: Iterable[S]):  # type: ignore
        for p in processed:
            super()._send_to_next(p)
