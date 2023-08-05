from multiprocessing import Queue
from typing import Callable, TypeVar

from .generic import GenericPipe

R = TypeVar("R")
S = TypeVar("S")


class TaskPipe(GenericPipe[R, S]):
    def __init__(self, source: "Queue[R]", task: Callable[[R], S], target: "Queue[S]"):
        super().__init__(source, target)
        self._task = task

    def _perform_task(self, data: R) -> S:
        return self._task(data)
