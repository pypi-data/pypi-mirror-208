from multiprocessing import Queue
import queue
from typing import Iterable, List, Optional, TypeVar

from .generic import GenericPipe

R = TypeVar("R")


class BatchPipe(GenericPipe[R, Iterable[R]]):
    def __init__(
        self,
        source: "Queue[R]",
        target: "Queue[Iterable[R]]",
        batch_size: int,
        keep_incomplete_batch: bool,
    ):
        super().__init__(source, target)
        self._batch_size = batch_size
        self._datas: List[R] = []
        self._keep_incomplete_batch = keep_incomplete_batch

    def _perform_task(self, data: R) -> Optional[Iterable[R]]:  # type: ignore
        self._datas.append(data)
        if len(self._datas) >= self._batch_size:
            packet, self._datas = (
                self._datas[: self._batch_size],
                self._datas[self._batch_size :],
            )
            return packet

    def _send_to_next(self, processed: Optional[Iterable[R]]) -> None:
        if processed is None:
            return
        super()._send_to_next(processed)

    def run(self):
        while True:
            try:
                data = self._source.get(timeout=self._timeout)
                if GenericPipe.is_death_packet(data):
                    if self._keep_incomplete_batch:
                        self._send_to_next(self._datas)
                    self._kill(data)
                    return
                processed = self._perform_task(data)
                self._send_to_next(processed)
            except queue.Empty:
                continue
            except Exception as e:
                self._kill(GenericPipe.get_kill_word())
                print(f"Error_{e.__class__.__name__}_{e.args}")
                return
