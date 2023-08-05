import queue
import time
from multiprocessing import Process, Queue
from queue import Empty
from threading import Timer
from typing import Any, Generic, Optional, Tuple, TypeVar, cast

R = TypeVar("R")
S = TypeVar("S")


class GenericPipe(Process, Generic[R, S]):
    __kill_word: Any = Empty

    def __init__(self, source: "Queue[R]", target: "Queue[S]"):
        super().__init__(daemon=True)
        self._source = source
        self._target = target
        self._timeout: Optional[float] = 0.1
        Timer(0.01, self.start).start()

    @staticmethod
    def is_death_packet(p: Any) -> bool:
        try:
            return p[0] is GenericPipe.__kill_word
        except Exception:
            return False

    @staticmethod
    def get_kill_word(count: int = 1) -> Any:
        return (GenericPipe.__kill_word, count)

    def get_ends(self) -> "Tuple[Queue[R], Process, Queue[S]]":
        return (self._source, self, self._target)

    def _close_source(self):
        try:
            self._source.close()
        except Exception:
            self.kill()

    def _kill(self, data: Any, error: bool = False):
        if error:
            while not self._target.empty():
                time.sleep(0.01)
        self._close_source()
        self._target.put(data)
        self._target.close()

    def _perform_task(self, data: R) -> S:
        return cast(S, data)

    def _send_to_next(self, processed: S):
        while True:
            try:
                self._target.put(processed, timeout=self._timeout)
                break
            except Exception as e:
                pass

    def run(self):
        while True:
            try:
                data = self._source.get(timeout=self._timeout)
                if GenericPipe.is_death_packet(data):
                    self._kill(data)
                    return
                processed = self._perform_task(data)
                self._send_to_next(processed)
            except queue.Empty:
                continue
            except Exception as e:
                self._kill(GenericPipe.get_kill_word(), True)
                print(f"Error_{e.__class__.__name__}_{e.args}")
                return
