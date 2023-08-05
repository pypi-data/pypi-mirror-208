import queue
from multiprocessing import Queue
from typing import Callable, TypeVar

from .generic import GenericPipe

R = TypeVar("R")
T = TypeVar("T")


class ReducePipe(GenericPipe[R, T]):
    def __init__(
        self,
        source: "Queue[R]",
        target: "Queue[T]",
        accumulator: T,
        reducer: Callable[[R, T], T],
    ):
        super().__init__(source, target)
        self._accumulator = accumulator
        self._reduce_function = reducer

    def _perform_task(self, data: R) -> None:  # type: ignore
        self._accumulator = self._reduce_function(data, self._accumulator)

    def run(self):
        while True:
            try:
                data = self._source.get(timeout=self._timeout)
                if GenericPipe.is_death_packet(data):
                    self._send_to_next(self._accumulator)
                    self._kill(data)
                    return
                self._perform_task(data)
            except queue.Empty:
                continue
            except Exception as e:
                self._kill(GenericPipe.get_kill_word())
                print(f"Error_{e.__class__.__name__}_{e.args}")
                return
