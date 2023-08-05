from multiprocessing import Queue
from typing import Callable, TypeVar

from .generic import GenericPipe

R = TypeVar("R")


class FilterPipe(GenericPipe[R, R]):
    def __init__(
        self, source: "Queue[R]", task: Callable[[R], bool], target: "Queue[R]"
    ):
        super().__init__(source, target)
        self._task = task

    def _perform_task(self, data: R) -> R:
        if self._task(data):
            super()._send_to_next(data)
        return data

    def _send_to_next(self, processed: R):
        pass
